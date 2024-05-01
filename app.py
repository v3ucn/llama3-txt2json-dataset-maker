import os
import json
import gradio as gr


def readtextfile(filename: str) -> list:
    lines = []
    with open(filename, 'r', encoding='utf-8') as in_file:
        line = in_file.readline()
        while line:
            lines.append(line)
            line = in_file.readline()
        return lines


def process_lines(lines: list, max_size: int) -> list:
    section = ""
    ret_list = []
    for idx in range(len(lines)):
        cur_line = lines[idx]
        cur_length = len(cur_line)
        if len(section) + cur_length < max_size:
            section += cur_line
        else:
            ret_list.append(section)
            section = cur_line
    return ret_list


def convert_records(sections: list) -> list:
    ret_list = []
    count = len(sections)
    if count % 2 != 0:
        count -= 1
    for idx in range(0, count, 2):
        record = {
            'instruction': '下列为一部小说中的一部分内容，请参照这部分内容，续写下一部分。',
            'input': sections[idx],
            'output': sections[idx + 1]
        }
        ret_list.append(record)
    return ret_list


def write_json(data: list, file_name: str):
    with open(file_name, 'w', encoding='utf-8') as out_fs:
        json.dump(data, out_fs, indent=4, ensure_ascii=False)


def filter_files(directory: str, extension: str) -> list:
    files = os.listdir(directory)
    filtered_files = [file for file in files if file.endswith(extension)]
    return filtered_files


def gen_json(file_path):

    path = file_path
    records = []
    files = filter_files(path, '.txt')

    for file in files:

        lines = readtextfile(path + file)
        
        sections = process_lines(lines, 512)
        items = convert_records(sections)
        for item in items:
            records.append(item)
        print('process file {} records: {}'.format(file, len(items)))
    print(f"共有{len(records)}条训练集")
    write_json(records, f'{file_path}dataset.json')

    text = ""
    with open(f'{file_path}dataset.json', 'r',encoding='utf-8') as f:
        text = f.read()


    return text,f"共有{len(records)}条训练集"




if __name__ == '__main__':


    with gr.Blocks() as demo:
        gr.Markdown('# 文本转数据集工具')
        with gr.Group():
            
            text_s = gr.Textbox(label="文本路径",value="./novel/")

            btn = gr.Button('开始转换', variant='primary')

            text_num = gr.Textbox(label="数据集条数",value="共有0条数据集")

            text_r = gr.Textbox(label="转换结果",value="", lines=16, max_lines=16)

            btn.click(gen_json,[text_s],[text_r,text_num])

    demo.queue().launch(inbrowser=True,server_name="0.0.0.0",)


    