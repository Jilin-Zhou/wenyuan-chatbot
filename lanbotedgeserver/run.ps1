conda activate lanbot
$filePath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$filePath += "/edge_server/main.py"
$env:CHATIE_API_URL="http://127.0.0.1:1090/chatbot/api/v1.0/get"
python $filePath
