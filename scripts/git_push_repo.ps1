Set-StrictMode -Version Latest
Set-Location -Path 'C:/Users/ander/OneDrive/Documents/RAG_BRH'

$s = git status --porcelain
if ($s) {
    git add -A
    git commit -m 'Add README, assets placeholder and process_downloads improvements; docs and visualizer'
} else {
    Write-Host 'No changes to commit'
}

if (git remote | Select-String 'origin') {
    git remote set-url origin https://github.com/Denart97/Ha-ti-Data-Intelligence
} else {
    git remote add origin https://github.com/Denart97/Ha-ti-Data-Intelligence
}

$branch = git rev-parse --abbrev-ref HEAD
git push -u origin $branch
