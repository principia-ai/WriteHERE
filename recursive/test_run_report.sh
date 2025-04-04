MODEL=claude-3-5-sonnet-20241022
# MODEL=gpt-4o
task_input_file=../test_data/qa_test.jsonl
output_folder=project/qa/example_claude/$MODEL/test_4turns

mkdir -p ${output_folder}
task_output_file=${output_folder}/result.jsonl
done_file=${output_folder}/done.txt


python engine.py --filename $task_input_file --output-filename $task_output_file --done-flag-file $done_file --model ${MODEL} --engine-backend google --mode report