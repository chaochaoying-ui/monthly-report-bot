# 月报机器人环境自动安装脚本
# PowerShell脚本 - 需要管理员权限

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "月报机器人 v1.3.1 环境自动安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否有管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告: 建议以管理员身份运行此脚本" -ForegroundColor Yellow
    Write-Host "按回车继续，或按Ctrl+C取消..." -ForegroundColor Yellow
    Read-Host
}

# 步骤1: 检查Python安装
Write-Host "[1/5] 检查Python安装..." -ForegroundColor Green
$pythonCmd = $null

# 尝试各种Python命令
$pythonCommands = @("python", "python3", "py")
foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "  ✓ 找到Python: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "  ✗ 未找到Python安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "正在下载Python 3.11.9..." -ForegroundColor Yellow
    
    $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-3.11.9-amd64.exe"
    
    try {
        # 下载Python安装包
        Write-Host "  下载地址: $pythonUrl" -ForegroundColor Gray
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        Write-Host "  ✓ Python安装包下载完成" -ForegroundColor Green
        
        # 静默安装Python
        Write-Host "  正在安装Python（可能需要几分钟）..." -ForegroundColor Yellow
        $installArgs = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1"
        Start-Process -FilePath $pythonInstaller -ArgumentList $installArgs -Wait -NoNewWindow
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # 再次检查Python
        Start-Sleep -Seconds 3
        try {
            $version = & python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = "python"
                Write-Host "  ✓ Python安装成功: $version" -ForegroundColor Green
            } else {
                throw "Python安装后仍无法使用"
            }
        } catch {
            Write-Host "  ✗ Python安装可能需要重启系统后生效" -ForegroundColor Red
            Write-Host "  请重启电脑后重新运行此脚本" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "或者手动安装Python: https://www.python.org/downloads/" -ForegroundColor Yellow
            Read-Host "按回车键退出"
            exit 1
        }
        
        # 清理安装包
        Remove-Item -Path $pythonInstaller -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "  ✗ Python下载/安装失败: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "请手动安装Python 3.11:" -ForegroundColor Yellow
        Write-Host "  1. 访问: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "  2. 下载Python 3.11.9" -ForegroundColor White
        Write-Host "  3. 安装时勾选 'Add Python to PATH'" -ForegroundColor White
        Write-Host "  4. 安装完成后重新运行此脚本" -ForegroundColor White
        Read-Host "按回车键退出"
        exit 1
    }
}

Write-Host ""

# 步骤2: 升级pip
Write-Host "[2/5] 升级pip..." -ForegroundColor Green
try {
    & $pythonCmd -m pip install --upgrade pip --quiet
    Write-Host "  ✓ pip升级完成" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ pip升级失败，继续..." -ForegroundColor Yellow
}

Write-Host ""

# 步骤3: 检查并安装依赖
Write-Host "[3/5] 安装项目依赖..." -ForegroundColor Green

$requirementsFile = "requirements_v1_1.txt"
if (Test-Path $requirementsFile) {
    Write-Host "  安装依赖包（可能需要几分钟）..." -ForegroundColor Gray
    try {
        & $pythonCmd -m pip install -r $requirementsFile --quiet
        Write-Host "  ✓ 依赖包安装完成" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ 部分依赖包安装失败，尝试逐个安装..." -ForegroundColor Yellow
        
        # 核心依赖
        $coreDeps = @(
            "lark-oapi>=1.4.22",
            "pytz",
            "pyyaml",
            "requests"
        )
        
        foreach ($dep in $coreDeps) {
            try {
                Write-Host "    安装 $dep..." -ForegroundColor Gray
                & $pythonCmd -m pip install $dep --quiet
                Write-Host "    ✓ $dep" -ForegroundColor Green
            } catch {
                Write-Host "    ✗ $dep 安装失败" -ForegroundColor Red
            }
        }
        
        # 可选依赖
        Write-Host "  安装可选依赖（图表功能）..." -ForegroundColor Gray
        $optionalDeps = @("matplotlib", "pandas", "numpy")
        foreach ($dep in $optionalDeps) {
            try {
                & $pythonCmd -m pip install $dep --quiet 2>&1 | Out-Null
                Write-Host "    ✓ $dep" -ForegroundColor Green
            } catch {
                Write-Host "    - $dep (可选，跳过)" -ForegroundColor DarkGray
            }
        }
    }
} else {
    Write-Host "  ⚠ 未找到requirements文件，手动安装核心依赖..." -ForegroundColor Yellow
    & $pythonCmd -m pip install lark-oapi pytz pyyaml requests --quiet
}

Write-Host ""

# 步骤4: 验证环境变量
Write-Host "[4/5] 验证环境变量配置..." -ForegroundColor Green

if (Test-Path "set_environment.ps1") {
    $envContent = Get-Content "set_environment.ps1" -Raw
    if ($envContent -match 'APP_ID.*=.*"([^"]+)"') {
        Write-Host "  ✓ APP_ID: $($Matches[1])" -ForegroundColor Green
    }
    if ($envContent -match 'CHAT_ID.*=.*"([^"]+)"') {
        Write-Host "  ✓ CHAT_ID: $($Matches[1])" -ForegroundColor Green
    }
    Write-Host "  ✓ 环境变量配置文件存在" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 未找到环境变量配置文件" -ForegroundColor Yellow
}

Write-Host ""

# 步骤5: 测试运行
Write-Host "[5/5] 测试Python环境..." -ForegroundColor Green

$testScript = @"
import sys
print(f'Python版本: {sys.version}')

try:
    import lark_oapi
    print('✓ lark-oapi')
except:
    print('✗ lark-oapi (未安装)')

try:
    import pytz
    print('✓ pytz')
except:
    print('✗ pytz (未安装)')

try:
    import yaml
    print('✓ pyyaml')
except:
    print('✗ pyyaml (未安装)')

try:
    import matplotlib
    print('✓ matplotlib (图表功能)')
except:
    print('- matplotlib (图表功能，可选)')

print('\n环境检查完成！')
"@

$testScript | & $pythonCmd 2>&1 | ForEach-Object {
    if ($_ -match '✓') {
        Write-Host "  $_" -ForegroundColor Green
    } elseif ($_ -match '✗') {
        Write-Host "  $_" -ForegroundColor Red
    } elseif ($_ -match '-') {
        Write-Host "  $_" -ForegroundColor DarkGray
    } else {
        Write-Host "  $_" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ 环境安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "启动方式：" -ForegroundColor Yellow
Write-Host "  1. 运行: start_bot.bat" -ForegroundColor White
Write-Host "  2. 或: $pythonCmd monthly_report_bot_final_interactive.py" -ForegroundColor White
Write-Host ""

# 询问是否立即启动
$response = Read-Host "是否立即启动机器人？(Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "正在启动月报机器人..." -ForegroundColor Green
    & .\start_bot.bat
} else {
    Write-Host ""
    Write-Host "稍后可运行 start_bot.bat 启动机器人" -ForegroundColor Yellow
}

Read-Host "按回车键退出"


