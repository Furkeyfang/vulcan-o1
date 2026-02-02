import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm  # 进度条
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type  # 重试机制

# 配置
API_KEY = "sk-deb21086a58f451fb27e82ebff71c072"
BASE_URL = "https://api.deepseek.com"
INPUT_JSONL_PATH = "level3.jsonl"
OUTPUT_JSONL_PATH = "eval_level3.jsonl"
MAX_WORKERS = 10  # 并发线程数（建议 5-20，太高容易触发 429 限流）

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

prompt = """
# Role
You are an expert Mechanical Engineer and a Senior Blender Developer. Your mission is to generate high-quality synthetic training data for a 7B parameter LLM. The data must demonstrate rigorous physical reasoning and executable, headless-compatible Blender Python (bpy) code.

# Operational Constraints (CRITICAL)
1. **Headless Execution**: The code MUST be compatible with Blender's background mode (`blender --background`). 
   - DO NOT use `bpy.context.space_data`, `bpy.ops.view3d`, or any UI-related context.
   - For visualization, use `bpy.ops.render.render` if necessary, but focus on object creation and physics setup.
2. **Linear Rigorous Reasoning**: Provide a direct, perfect, and step-by-step solution. Do not include trial-and-error or self-correction. Focus on "getting it right the first time" through precise calculation.
3. **Variable-Driven Code**: In the `implementation` block, extract all numerical values from the `parameter_summary` as variables first. Do not hardcode numbers directly into Blender operators.

# Thinking Structure (Strict XML)
You must wrap the response in the following XML tags:
<strategic_analysis>
Qualitative analysis of the task. Explain the mechanical principle chosen (e.g., lever, catapult, truss).
</strategic_analysis>

<spatial_layout>
Quantitative geometric derivation. Show mathematical formulas (e.g., "Pivot_Z = Obstacle_H + Margin"). Explain the "why" behind every coordinate.
</spatial_layout>

<kinematic_topology>
Define the structural hierarchy and joint types (e.g., Base [Static] -> Hinge Joint -> Arm [Rigid Body]).
</kinematic_topology>

<predictive_simulation>
Proactive physical assessment. Mention stability, center of mass, and anticipated trajectory. Explain how the design "pre-emptively" avoids failure (e.g., "Widened base to prevent tipping").
</predictive_simulation>

<parameter_summary>
A clean list of all key-value pairs (variables and their values) used for the design.
</parameter_summary>

<implementation>
```python
# Headless-compatible bpy code
# 1. Import modules
# 2. Define variables from summary
# 3. Clear scene
# 4. Build geometry and apply physics
```
</implementation>

# One-Shot Example
Task: Place a 4x4x0.5 platform at (0,0,5) and a 1m radius sphere on top of it. Both should have physics.

<strategic_analysis>
The goal is a static platform holding a dynamic sphere at a specific height. I will use a passive rigid body for the platform and an active one for the sphere to simulate gravity.
</strategic_analysis>

<spatial_layout>
- Platform: Size (4,4,0.5). Center at (0,0,5).
- Sphere: Radius 1.0. To place it exactly on the platform, Sphere_Z = Platform_Z + (Platform_Thickness/2) + Sphere_Radius = 5 + 0.25 + 1.0 = 6.25.
- World Origin is at Z=0.
</spatial_layout>

<kinematic_topology>
- World -> Platform (Passive Rigid Body)
- World -> Sphere (Active Rigid Body, positioned above Platform)
</kinematic_topology>

<predictive_simulation>
The sphere will drop due to gravity. The platform must be "Passive" to remain fixed in mid-air. The collision margin should be default to ensure contact stability at Z=6.25.
</predictive_simulation>

<parameter_summary>
- platform_dim: (4.0, 4.0, 0.5)
- platform_loc: (0.0, 0.0, 5.0)
- sphere_radius: 1.0
- sphere_loc: (0.0, 0.0, 6.25)
</parameter_summary>

<implementation>
```python
import bpy

# Clear scene
if bpy.context.object:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Variables from summary
p_dim = (4.0, 4.0, 0.5)
p_loc = (0.0, 0.0, 5.0)
s_rad = 1.0
s_loc = (0.0, 0.0, 6.25)

# Create Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=p_loc)
plat = bpy.context.active_object
plat.scale = p_dim
bpy.ops.rigidbody.object_add()
plat.rigid_body.type = 'PASSIVE'

# Create Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=s_rad, location=s_loc)
bpy.ops.rigidbody.object_add()
# The sphere is 'ACTIVE' by default
```
</implementation>
"""

# 增加重试机制：如果报错，等待 1-10秒后重试，最多试 5 次
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception) # 任何异常都重试
)
def eval_pair_safe(modern):
    user_prompt = f"""Here is a task description: {modern}"""

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": user_prompt}],
        response_format={"type": "text"},
        timeout=60 # 设置超时防止卡死
    )
    return response.choices[0].message.content

def process_line(line_data):
    """
    单个任务的处理逻辑
    """
    try:
        if "id" not in line_data:
            return None
            
        modern = line_data["instruction"]
        
        
        # 调用 API
        eval_result = eval_pair_safe(modern)
        eval_result = {
            "answer": eval_result
        }
        # 合并结果
        # 注意：这里我们把原始 id 也带上，方便后续如果顺序乱了可以重新排序，
        # 或者直接保存 line_data 的所有信息 + eval 结果
        result_data = line_data.copy() 
        result_data.update(eval_result) # 把 eval 的字段加进去
        
        return result_data
        
    except Exception as e:
        print(f"\nError processing ID {line_data.get('id', 'unknown')}: {e}")
        return None

def process_jsonl_parallel(input_path, output_path):
    # 1. 读取所有数据到内存（假设文件不是几个G那么大，普通 JSONL 没问题）
    print("正在读取文件...")
    data_lines = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data_lines.append(json.loads(line.strip()))
                except:
                    pass
    
    total_lines = len(data_lines)
    print(f"共读取到 {total_lines} 条数据，准备开始并发处理...")

    # 2. 准备输出文件（清空旧文件）
    with open(output_path, "w", encoding="utf-8") as f:
        pass # Just truncate

    # 3. 使用 ThreadPoolExecutor 并行处理
    # 使用 Lock 确保写入文件时不冲突
    write_lock = threading.Lock()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_id = {executor.submit(process_line, item): item['id'] for item in data_lines}
        
        # 使用 tqdm 显示进度条
        with open(output_path, "a", encoding="utf-8") as f_out:
            for future in tqdm(as_completed(future_to_id), total=total_lines, desc="Evaluating"):
                result = future.result()
                if result:
                    # 写入文件（加锁）
                    with write_lock:
                        f_out.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"处理完成！结果已保存到：{output_path}")

if __name__ == "__main__":
    process_jsonl_parallel(INPUT_JSONL_PATH, OUTPUT_JSONL_PATH)
