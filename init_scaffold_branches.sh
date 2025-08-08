#!/bin/bash

set -e
echo "Initializing branch: infra/repo-hygiene-ci"
git checkout main
git pull
git checkout -b infra/repo-hygiene-ci
mkdir -p .scaffold
echo "# PR1 - Repo hygiene & CI skeleton" > .scaffold/TASK_infra_repo-hygiene-ci.md
git add .scaffold/TASK_infra_repo-hygiene-ci.md
git commit -m "init: scaffold PR1 - Repo hygiene & CI skeleton"
git push -u origin infra/repo-hygiene-ci

echo "Initializing branch: feat/data-pipeline-parquet"
git checkout main
git pull
git checkout -b feat/data-pipeline-parquet
mkdir -p .scaffold
echo "# PR2 - Data pipeline v1 (CSV->Parquet cache + Polars)" > .scaffold/TASK_feat_data-pipeline-parquet.md
git add .scaffold/TASK_feat_data-pipeline-parquet.md
git commit -m "init: scaffold PR2 - Data pipeline v1 (CSV->Parquet cache + Polars)"
git push -u origin feat/data-pipeline-parquet

echo "Initializing branch: feat/config-validation-column-mapping"
git checkout main
git pull
git checkout -b feat/config-validation-column-mapping
mkdir -p .scaffold
echo "# PR3 - Config validation + Column Mapping UI" > .scaffold/TASK_feat_config-validation-column-mapping.md
git add .scaffold/TASK_feat_config-validation-column-mapping.md
git commit -m "init: scaffold PR3 - Config validation + Column Mapping UI"
git push -u origin feat/config-validation-column-mapping

echo "Initializing branch: perf/lod-decimator"
git checkout main
git pull
git checkout -b perf/lod-decimator
mkdir -p .scaffold
echo "# PR4 - Performance/LOD (decimator + payload cap + slider)" > .scaffold/TASK_perf_lod-decimator.md
git add .scaffold/TASK_perf_lod-decimator.md
git commit -m "init: scaffold PR4 - Performance/LOD (decimator + payload cap + slider)"
git push -u origin perf/lod-decimator

echo "Initializing branch: feat/voxel-isosurface"
git checkout main
git pull
git checkout -b feat/voxel-isosurface
mkdir -p .scaffold
echo "# PR5 - Voxelization + Isosurface Mode" > .scaffold/TASK_feat_voxel-isosurface.md
git add .scaffold/TASK_feat_voxel-isosurface.md
git commit -m "init: scaffold PR5 - Voxelization + Isosurface Mode"
git push -u origin feat/voxel-isosurface

echo "Initializing branch: feat/roi-crossfilter"
git checkout main
git pull
git checkout -b feat/roi-crossfilter
mkdir -p .scaffold
echo "# PR6 - ROI Selection + Crossfilter" > .scaffold/TASK_feat_roi-crossfilter.md
git add .scaffold/TASK_feat_roi-crossfilter.md
git commit -m "init: scaffold PR6 - ROI Selection + Crossfilter"
git push -u origin feat/roi-crossfilter

echo "Initializing branch: feat/error-panel-progress"
git checkout main
git pull
git checkout -b feat/error-panel-progress
mkdir -p .scaffold
echo "# PR7 - Error Panel + Progress/Cancel UX" > .scaffold/TASK_feat_error-panel-progress.md
git add .scaffold/TASK_feat_error-panel-progress.md
git commit -m "init: scaffold PR7 - Error Panel + Progress/Cancel UX"
git push -u origin feat/error-panel-progress

echo "Initializing branch: feat/session-export"
git checkout main
git pull
git checkout -b feat/session-export
mkdir -p .scaffold
echo "# PR8 - Session Save/Load + Export" > .scaffold/TASK_feat_session-export.md
git add .scaffold/TASK_feat_session-export.md
git commit -m "init: scaffold PR8 - Session Save/Load + Export"
git push -u origin feat/session-export

echo "Initializing branch: test/suite-upgrade"
git checkout main
git pull
git checkout -b test/suite-upgrade
mkdir -p .scaffold
echo "# PR9 - Test Suite Upgrade" > .scaffold/TASK_test_suite-upgrade.md
git add .scaffold/TASK_test_suite-upgrade.md
git commit -m "init: scaffold PR9 - Test Suite Upgrade"
git push -u origin test/suite-upgrade

echo "Initializing branch: release/windows-packaging"
git checkout main
git pull
git checkout -b release/windows-packaging
mkdir -p .scaffold
echo "# PR10 - Windows Packaging & Release CI" > .scaffold/TASK_release_windows-packaging.md
git add .scaffold/TASK_release_windows-packaging.md
git commit -m "init: scaffold PR10 - Windows Packaging & Release CI"
git push -u origin release/windows-packaging

echo "Initializing branch: docs/demo-data"
git checkout main
git pull
git checkout -b docs/demo-data
mkdir -p .scaffold
echo "# PR11 - Docs + Demo Data" > .scaffold/TASK_docs_demo-data.md
git add .scaffold/TASK_docs_demo-data.md
git commit -m "init: scaffold PR11 - Docs + Demo Data"
git push -u origin docs/demo-data

echo "Initializing branch: feat/watch-folder"
git checkout main
git pull
git checkout -b feat/watch-folder
mkdir -p .scaffold
echo "# PR12 - Watch Folder / Live Reload" > .scaffold/TASK_feat_watch-folder.md
git add .scaffold/TASK_feat_watch-folder.md
git commit -m "init: scaffold PR12 - Watch Folder / Live Reload"
git push -u origin feat/watch-folder

echo "Initializing branch: infra/linux-container-devcontainer"
git checkout main
git pull
git checkout -b infra/linux-container-devcontainer
mkdir -p .scaffold
echo "# PR13 - Linux Containerization & Devcontainer" > .scaffold/TASK_infra_linux-container-devcontainer.md
git add .scaffold/TASK_infra_linux-container-devcontainer.md
git commit -m "init: scaffold PR13 - Linux Containerization & Devcontainer"
git push -u origin infra/linux-container-devcontainer
