$ErrorActionPreference = 'Stop'
Set-Location 'C:\Users\drkim\.openclaw\workspace\diablo4-dashboard'
$python = 'C:\Users\drkim\AppData\Local\Programs\Python\Python313\python.exe'
$arguments = '-m streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8535'
Start-Process -FilePath $python -ArgumentList $arguments -WindowStyle Hidden
