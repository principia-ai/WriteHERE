
INPUT_FILE1=/path/to/input/file1.jsonl


OUTPUT_FILE=/path/to/output/file.jsonl
JUDEG_MODEL=to_judge_model

# The json object should have the following fields:
# prompt, to_eval_article

python report_eval.py --filename ${INPUT_FILE1} --output-filename ${OUTPUT_FILE} --model ${JUDEG_MODEL} | tee ${OUTPUT_FILE}.log