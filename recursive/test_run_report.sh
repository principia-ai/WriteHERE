# MODEL=claude-3-5-sonnet-20241022
# MODEL=gpt-4o
# MODEL=gemini-2.5-pro-exp-03-25
MODEL=google/gemini-2.5-pro-preview-03-25
task_input_file=../test_data/qa_test.jsonl
output_folder=project/report/example_gemini/$MODEL/gemini-2.5

mkdir -p ${output_folder}
task_output_file=${output_folder}/result.jsonl
done_file=${output_folder}/done.txt


python engine.py --filename $task_input_file --output-filename $task_output_file --done-flag-file $done_file --model ${MODEL} --engine-backend google --mode report