
@echo off
REM �o�b�`�t�@�C���̂���f�B���N�g���Ɉړ�
cd /d %~dp0

REM fix_frontmatter_dates.bat �����s���A�I����҂�
call fix_frontmatter_dates.bat

REM 2�b�ҋ@
timeout /t 2 /nobreak >nul

start gemini -m gemini-2.5-flash -p "@gemini_command.md�̓��e�����s���āB��ʂɂ͐i���ȊO�̏�񂪏o���K�v�͂���܂���" -y


