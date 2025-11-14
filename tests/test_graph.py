from WriteHERE.backend.server import transform_node_to_graph




def test_transform_node_to_graph_basic():
    node = {
        "nid": "123",
        "status": "DONE",
        "node_type": "EXECUTE_NODE",
        "task_info": {
            "goal": "Test goal",
            "task_type": "execution",
        },
        "result": {
            "ACTION_1": {"result": {"result": "success"}, "time": "1"},
            "ACTION_2": {"result": {"result": "final"}, "time": "2"},
        },
    }

    out = transform_node_to_graph(node)

    assert out["id"] == "123"
    assert out["goal"] == "Test goal"
    assert out["task_type"] == "execution"
    assert out["is_execute_node"] is True


    assert len(out["actions"]) == 2


    assert out["latest_action"]["name"] == "ACTION_2"
    assert out["latest_action"]["result"] == "final"
