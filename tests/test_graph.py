from WriteHERE.backend.server import transform_node_to_graph

def test_transform_node_to_graph_basic():
    # Fake node data similar to what your backend uses
    node = {
        "nid": "123",
        "status": "DONE",
        "node_type": "EXECUTE_NODE",
        "task_info": {
            "goal": "Test goal",
            "task_type": "execution",
            "dependency": ["A", "B"]
        },
        "result": {
            "ACTION_1": {
                "result": {"result": "success"},
                "time": "2025-01-01T01:00:00Z"
            },
            "ACTION_2": {
                "result": {"result": "final"},
                "time": "2025-01-01T02:00:00Z"
            }
        }
    }

    output = transform_node_to_graph(node)

    # Assertions
    assert output["id"] == "123"
    assert output["goal"] == "Test goal"
    assert output["task_type"] == "execution"
    assert output["status"] == "DONE"
    assert output["node_type"] == "EXECUTE_NODE"
    assert output["is_execute_node"] is True

    # Verify actions collected
    assert len(output["actions"]) == 2

    # Verify latest action
    assert output["latest_action"]["name"] == "ACTION_2"
    assert output["latest_action"]["result"] == "final"
