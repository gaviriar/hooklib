ctags -R -f .git/tags --python-kinds=-i --exclude=.git --exclude=log . $(python -c "import os, sys; print(' '.join('{}'.format(d) for d in sys.path if os.path.isdir(d)))")
