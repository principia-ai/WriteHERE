
INPUT_FILE1=/path/to/input/model1_file.jsonl
INPUT_FILE2=/path/to/input/model2_file.jsonl

MODE1=model1
MODE2=model2


OUTPUT_FOLDER=/path/to/output/folder
JUDEG_MODEL=to_judge_model

# The json object should have the following fields:
# id, result, 
# GSB calculation
python novel_gsb.py --filenames ${INPUT_FILE1},${INPUT_FILE2} --output-folder ${OUTPUT_FOLDER} --model-names ${MODE1},${MODE2} | tee ${OUTPUT_FOLDER}/log.txt

# Elo calculation
python calculate_elo.py --input-files ${OUTPUT_FOLDER}/pk_gather.jsonl --output-folder ${OUTPUT_FOLDER} | tee ${OUTPUT_FOLDER}/log.txt

