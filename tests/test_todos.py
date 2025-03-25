from fastapi import status


def test_create_valid_todo(client, token, mock_valid_todo):
    response = client.post(
        "/todos",
        headers={"Authorization": f"Bearer {token}"},
        json=mock_valid_todo
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == dict(**mock_valid_todo, id=1)
