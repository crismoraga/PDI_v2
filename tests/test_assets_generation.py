def test_generate_celebration_gif_runs(tmp_path):
    import subprocess
    import sys
    # just run the script; it will write into assets/ui
    res = subprocess.run([sys.executable, 'tools/generate_celebration_gif.py'])
    assert res.returncode == 0
