# MODEL=claude-3-7-sonnet-20250219
MODEL=gpt-4o
task_input_file=../test_data/meta_fiction.jsonl
output_folder=project/story/$MODEL/reorder_prompts/meta_fiction_grief
mkdir -p ${output_folder}
task_output_file=${output_folder}/result.jsonl
done_file=${output_folder}/done.txt

python engine.py --filename $task_input_file --output-filename $task_output_file --done-flag-file $done_file --model ${MODEL} --mode story --language 'en'
