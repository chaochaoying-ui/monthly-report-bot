# Python 3.11.9 自动下载和安装脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Python 3.11.9 自动下载和安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python下载链接
$pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
$pythonInstaller = "$env:USERPROFILE\Downloads\python-3.11.9-amd64.exe"

Write-Host "正在下载Python 3.11.9..." -ForegroundColor Yellow
Write-Host "下载地址: $pythonUrl" -ForegroundColor Gray
Write-Host "保存位置: $pythonInstaller" -ForegroundColor Gray
Write-Host ""

try {
    # 显示下载进度
    $ProgressPreference = 'Continue'
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
    
    Write-Host "✓ Python安装包下载完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "开始安装Python（需要管理员权限）..." -ForegroundColor Yellow
    Write-Host ""
    
    # 静默安装Python（所有用户 + 添加到PATH）
    $installArgs = @(
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Include_test=0",
        "Include_pip=1",
        "Include_doc=0",
        "SimpleInstall=1"
    )
    
    $process = Start-Process -FilePath $pythonInstaller -ArgumentList $installArgs -Wait -PassThru -Verb RunAs
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✓ Python安装成功！" -ForegroundColor Green
        Write-Host ""
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # 验证安装
        Start-Sleep -Seconds 2
        try {
            $version = python --version 2>&1
            Write-Host "Python版本: $version" -ForegroundColor Green
        } catch {
            Write-Host "提示: Python已安装，但可能需要重启系统或打开新的命令窗口才能使用" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "安装完成！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "下一步:" -ForegroundColor Yellow
        Write-Host "  1. 关闭当前窗口" -ForegroundColor White
        Write-Host "  2. 重新打开PowerShell" -ForegroundColor White
        Write-Host "  3. 运行: cd F:\monthly_report_bot_link_pack\monthly_report_bot_link_pack" -ForegroundColor White
        Write-Host "  4. 运行: .\install_environment.bat" -ForegroundColor White
        Write-Host ""
        
        # 清理安装包
        $cleanup = Read-Host "是否删除安装包？(Y/N)"
        if ($cleanup -eq 'Y' -or $cleanup -eq 'y') {
            Remove-Item -Path $pythonInstaller -Force
            Write-Host "✓ 安装包已删除" -ForegroundColor Green
        }
        
    } else {
        Write-Host "✗ Python安装失败，退出代码: $($process.ExitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "请尝试手动安装:" -ForegroundColor Yellow
        Write-Host "  1. 打开文件: $pythonInstaller" -ForegroundColor White
        Write-Host "  2. 运行安装程序" -ForegroundColor White
        Write-Host "  3. 勾选 'Add Python to PATH'" -ForegroundColor White
    }
    
} catch {
    Write-Host "✗ 下载/安装失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "手动下载地址:" -ForegroundColor Yellow
    Write-Host "  $pythonUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "或访问官网: https://www.python.org/downloads/" -ForegroundColor White
}

Write-Host ""
Read-Host "按回车键退出"



