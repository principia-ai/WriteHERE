import argparse 
from autoprompt.utils import auto_read
import numpy as np
from scipy.optimize import minimize
from collections import defaultdict


def parse_list(xs):
    return [x.strip() for x in xs.split(",")]

def get_item_id(item):
    return item["id"]
    # return "{}-{}".format(item["ori"]["example_id"], item["ori"]["inputs"])


def preprocess_data(data):
    """Convert raw data into matrix form, counting wins, losses and ties"""
    # Collect all model names and sort them
    models = set()
    for entry in data:
        models.add(entry['model_a'])
        models.add(entry['model_b'])
    models = sorted(models)
    K = len(models)
    name_to_idx = {name: i for i, name in enumerate(models)}
    
    # Initialize statistics matrices
    w = np.zeros((K, K), dtype=int)  # w[i][j] represents the number of times i wins against j
    d = np.zeros((K, K), dtype=int)  # d[i][j] represents the number of ties between i and j (only valid when i < j)
    
    # Fill in the data
    for entry in data:
        i = name_to_idx[entry['model_a']]
        j = name_to_idx[entry['model_b']]
        res = entry['result']
        
        # Handle wins and losses
        if res == "win":
            w[i, j] += 1
        elif res == "bad":
            w[j, i] += 1
        
        # Handle ties (ensure i < j storage)
        elif res == "tie":
            if i < j:
                d[i, j] += 1
            else:
                d[j, i] += 1
    
    return models, w, d

def negative_log_likelihood(params, w, d, K):
    """Calculate negative log likelihood (with numerical stability handling)"""
    lambdas = params[:K]
    nu = params[K]
    log_likelihood = 0.0
    
    for i in range(K):
        for j in range(i+1, K):  # Only process pairs where i < j
            if w[i,j] == 0 and w[j,i] == 0 and d[i,j] == 0:
                continue
            
            lambda_i = max(lambdas[i], 1e-6)  # Avoid division by zero
            lambda_j = max(lambdas[j], 1e-6)
            nu_val = max(nu, 1e-6)
            
            # Calculate common denominator
            sqrt_term = np.sqrt(lambda_i * lambda_j)
            denominator = lambda_i + lambda_j + nu_val * sqrt_term
            
            # Calculate probability terms (with numerical stability)
            eps = 1e-10  # Prevent log(0)
            p_win = lambda_i / (denominator + eps)
            p_lose = lambda_j / (denominator + eps)
            p_tie = (nu_val * sqrt_term) / (denominator + eps)
            
            # Accumulate log likelihood
            log_likelihood += w[i,j] * np.log(p_win + eps)
            log_likelihood += w[j,i] * np.log(p_lose + eps)
            log_likelihood += d[i,j] * np.log(p_tie + eps)
    
    return -log_likelihood

def fit_davidson_model(data):
    """Main function: Fit Davidson model parameters"""
    # Data preprocessing
    models, w, d = preprocess_data(data)
    K = len(models)
    
    # Initialize parameters: all lambda=1, nu=1
    initial_params = np.ones(K + 1)
    
    # Set parameter bounds (must be positive)
    bounds = [(1e-6, None)] * (K + 1)
    
    # Optimization (using L-BFGS-B method)
    result = minimize(
        negative_log_likelihood,
        initial_params,
        args=(w, d, K),
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 10000}
    )
    
    if not result.success:
        raise RuntimeError(f"Optimization failed: {result.message}")
    
    # Extract parameters and standardize
    lambdas = result.x[:K]
    nu = result.x[K]
    
    # Map parameters to model names
    return {
        'models': models,
        'lambda': lambdas / np.mean(lambdas),  # Standardize for interpretation
        'nu': nu
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-files", type=parse_list)
    
    args = parser.parse_args()
    # all_results = []
    keys = ("Plot", "Creativity", "Development", "Language_Use", "Overall")
    # Process all data
    all_results = {
        key: [] for key in keys
    }
    cnt = 0
    drop_cnt = 0
    for input_fn in args.input_files:
        data = auto_read(input_fn)
        # cur input round
        model_a = data[0]["all_eval_result"][0]["compare_keys"].split("&")[0]
        model_b = data[0]["all_eval_result"][0]["compare_keys"].split("&")[1]
        
        for item in data:
            item_id = get_item_id(item)
            ensemble_eval = item["ensemble_eval"]
            storys = [v  for k, v in item.items() if k.startswith("story_")]
            assert len(storys) == 2
            
            cnt += 1
            
            for key in keys:
                result = ensemble_eval[key]
                if result != "same":
                    assert result == model_a or result == model_b
                    if result == model_a:
                        all_results[key].append({
                            "model_a": model_a,
                            "model_b": model_b,
                            "result": "win"
                        })
                    else:
                        all_results[key].append({
                            "model_a": model_a,
                            "model_b": model_b,
                            "result": "bad"
                        })
                else:
                    all_results[key].append({
                        "model_a": model_a,
                        "model_b": model_b,
                        "result": "tie"
                    })
        
       
    print("Drop {}, final {}".format(drop_cnt, cnt)) 
    # Start Run
    for key in keys:
        # 运行模型
        result = fit_davidson_model(all_results[key])
        print(key)
        print("Model strength parameters (standardized):")
        for name, lam in zip(result['models'], result['lambda']):
            print(f"{name}: {lam:.4f}")
        print(f"Tie parameter nu: {result['nu']:.4f}")

            
            