def test_contract_app_interface():
    from zdex import run_app
    assert callable(run_app)
