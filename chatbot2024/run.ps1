# 创建虚拟环境，如果虚拟环境已存在则直接激活虚拟环境
conda info --envs | findstr botvenv
if ($LASTEXITCODE -eq 0) {
    conda create -n botvenv python=3.10
}
conda activate botvenv
# 安装依赖
pip install -r requirements.txt
# 设置环境变量并启动服务
$env:OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
$env:OPENAI_BASE_URL="YOUR_OPENAI_BASE_URL"
python app.py --port 1090
