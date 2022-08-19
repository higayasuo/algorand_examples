# from conftest import client
from typing import Iterator

from algosdk.v2client.algod import AlgodClient

import pytest

from helper import (
    read_global_state,
    create_app,
    delete_app,
    compile_smart_contract,
    call_app,
)
from accounts import test1_private_key

from counter_asc1 import (
    approval_program,
    clear_state_program,
    global_schema,
    local_schema,
    AppMethods,
)


@pytest.fixture
def app_id(client: AlgodClient) -> Iterator[int]:
    approval = compile_smart_contract(client, approval_program())
    clear = compile_smart_contract(client, clear_state_program())

    app_id = create_app(
        client,
        test1_private_key,
        approval,
        clear,
        global_schema,
        local_schema,
    )
    yield app_id

    delete_app(client, test1_private_key, app_id)


def test_counter_asc1(client: AlgodClient, app_id: int) -> None:
    state = read_global_state(client, app_id)
    assert state["count"] == 0

    app_args = [AppMethods.add]
    call_app(client, test1_private_key, app_id, app_args)
    state = read_global_state(client, app_id)
    assert state["count"] == 1

    app_args = [AppMethods.subtract]
    call_app(client, test1_private_key, app_id, app_args)
    state = read_global_state(client, app_id)
    assert state["count"] == 0
