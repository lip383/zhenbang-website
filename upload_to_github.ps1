# GitHub 文件上传脚本
# 使用 GitHub API 上传文件

$repoOwner = "lip383"
$repoName = "zhenbang-website"
$branch = "main"

# 需要修改的文件列表
$filesToUpload = @(
    "index.html",
    "history.html",
    "vote_standalone.html",
    "stats_standalone.html",
    "message.html",
    "lucky.html",
    "style.css",
    "main.js"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  振邦网站文件上传到 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "仓库: $repoOwner/$repoName" -ForegroundColor Yellow
Write-Host "分支: $branch" -ForegroundColor Yellow
Write-Host ""
Write-Host "需要上传的文件:" -ForegroundColor Green
$filesToUpload | ForEach-Object { Write-Host "  - $_" }
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请按以下步骤操作:" -ForegroundColor Yellow
Write-Host "1. 打开浏览器访问: https://github.com/$repoOwner/$repoName" -ForegroundColor White
Write-Host "2. 点击 'Add file' -> 'Upload files'" -ForegroundColor White
Write-Host "3. 将以下文件拖放到上传区域:" -ForegroundColor White
Write-Host ""
$filesToUpload | ForEach-Object { 
    $fullPath = Join-Path $PSScriptRoot $_
    Write-Host "   $fullPath" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "4. 填写提交信息，例如: '更新网站内容，完善发展历程'" -ForegroundColor White
Write-Host "5. 点击 'Commit changes'" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 打开 GitHub 仓库页面
Start-Process "https://github.com/$repoOwner/$repoName"

Read-Host "按 Enter 键退出..."
