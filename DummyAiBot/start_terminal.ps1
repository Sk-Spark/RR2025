# PowerShell script to start DummyAiBot in terminal mode
Write-Host "🚀 Starting DummyAiBot in Terminal Mode..." -ForegroundColor Green
Write-Host "This will allow you to control the bot directly from the console." -ForegroundColor Cyan
Write-Host "=" * 60

try {
    python main.py --terminal --bot-id "terminal_bot_001"
} catch {
    Write-Host "❌ Error starting bot: $_" -ForegroundColor Red
}

Write-Host "👋 Terminal mode stopped." -ForegroundColor Yellow
