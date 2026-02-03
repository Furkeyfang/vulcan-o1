import re
import json
import os

input_path = "eval_level2.jsonl"
OUTPUT_JSONL_PATH = "blender_codes_level2"

def convert_escaped_text_to_pure_python(raw_escaped_text):
    """
    终极修复：
    1. 彻底删除所有\转义符（包括\n里的\）
    2. 把\n字符转换成真实的换行符（不是字符串，是文本换行）
    3. 提取代码后，输出纯文本、无任何转义符的Python代码
    """
    # -------------------------- 步骤1：彻底清理所有转义符 --------------------------
    # 1. 先把字符串里的"\n"（两个字符：\ + n）替换成真实的换行符（\n）
    cleaned_text = raw_escaped_text.replace('\\n', '\n')
    # 2. 删除所有多余的反斜杠\（包括转义的\"、\\等）
    cleaned_text = cleaned_text.replace('\\', '')
    # -------------------------- 步骤2：精准匹配<implementation>标签 --------------------------
    impl_pattern = r"<implementation>\s*(.*?)\s*</implementation>"
    impl_match = re.search(impl_pattern, cleaned_text, re.DOTALL)
    if not impl_match:
        raise ValueError(f"❌ 未找到<implementation>标签，清理后文本前1000字符：{cleaned_text[:1000]}")
    impl_content = impl_match.group(1).strip()

    # -------------------------- 步骤3：提取Python代码块 --------------------------
    py_pattern = r"```python\s*(.*?)\s*```"
    py_match = re.search(py_pattern, impl_content, re.DOTALL)
    if not py_match:
        raise ValueError(f"❌ 未找到```python代码块，内容：{impl_content[:500]}")
    
    # 核心：提取的代码已经是真实换行，无任何转义符
    pure_python_code = py_match.group(1).strip()

    # -------------------------- 步骤4：清理代码格式（可选，让代码更易读） --------------------------
    
    # 修复单行过长的代码（比如cube创建行拆分成多行）
    pure_python_code = re.sub(
        r'(bpy\.ops\.mesh\.primitive_cube_add\(.*?\)) cube =',
        r'\1\ncube =',
        pure_python_code
    )
    # 适配Blender 3.3 LTS
    pure_python_code = pure_python_code.replace(
        "bpy.context.scene.rigidbody_world.steps_per_second = 60",
        "bpy.context.scene.rigidbody_world.time_scale = 1.0  # 3.3 LTS兼容"
    )
    
    return pure_python_code

# ====================== 主程序：处理JSONL并输出可直接运行的代码 =======================
if __name__ == "__main__":
    with open(input_path, "r", encoding="utf-8") as in_f:
        line_num = 0
        for line in in_f:
            line_num += 1
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                if 'answer' not in data:
                    print(f"第{line_num}行无answer字段，跳过")
                    continue
                
                # 转换代码（输出真实换行，无转义符）
                pure_code = convert_escaped_text_to_pure_python(data['answer'])
                
                py_file_path = os.path.join(OUTPUT_JSONL_PATH, f"{data['id']}.py")
                # 写入纯文本文件（关键：用utf-8编码，直接写真实换行）
                with open(py_file_path, "w", encoding="utf-8") as py_f:
                    py_f.write(pure_code)
                
                
                # 输出到JSONL（ensure_ascii=False保证换行符不被转义
                
                # 可选：打印提取的代码（验证无转义符）
                print(f"\n✅ 第{line_num}行提取成功，代码预览：")
                print(pure_code[:300] + "...")
                
            except json.JSONDecodeError as e:
                print(f"第{line_num}行JSON错误：{e}")
            except Exception as e:
                print(f"第{line_num}行处理失败：{e}，原始数据：{line[:500]}")
    
    print(f"\n📁 最终结果已保存至：{OUTPUT_JSONL_PATH}")
    print("💡 提示：输出的code字段是纯文本，可直接复制到Blender运行！")