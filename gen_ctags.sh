ctags -R -f .git/tags --python-kinds=-iv --exclude=.git --exclude=log $(pwd) $(python -c "import os, sys; print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))")
