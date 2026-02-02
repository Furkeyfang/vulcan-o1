import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
# 配置

INPUT_JSONL_PATH = "level2.jsonl"
OUTPUT_JSONL_PATH = "level2_1.jsonl"

def convert_format(input_path, OUTPUT_JSONL_PATH):
    with open(input_path, "r", encoding="utf-8") as in_f, \
         open(OUTPUT_JSONL_PATH, "w", encoding="utf-8") as out_f:

        line_num = 0
        for line in in_f:
            line_num += 1
            # 跳过空行
            if not line.strip():
                continue
            
            try:
                # 解析单行JSON
                data = json.loads(line.strip())
                output1 = {"id": line_num}
                output1.update(data)
                # 写入输出文件（单行JSON）
                out_f.write(json.dumps(output1, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                print(f"第{line_num}行JSON格式错误，跳过：{line.strip()}")
            except Exception as e:
                print(f"第{line_num}行处理失败：{str(e)}，原始数据：{line.strip()}")

if __name__ == "__main__":
    convert_format(INPUT_JSONL_PATH, OUTPUT_JSONL_PATH)