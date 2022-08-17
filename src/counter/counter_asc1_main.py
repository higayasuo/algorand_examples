from helper import (
    create_algod_client,
    compile_smart_contract,
    create_app,
    call_app,
    delete_app,
    read_global_state,
)
from accounts import test1_private_key as private_key
from counter_asc1 import (
    approval_program,
    clear_state_program,
    global_schema,
    local_schema,
    AppMethods,
)


def main() -> None:
    client = create_algod_client()

    approval = compile_smart_contract(client, approval_program())
    clear = compile_smart_contract(client, clear_state_program())

    app_id = create_app(
        client,
        private_key,
        approval,
        clear,
        global_schema,
        local_schema,
    )

    print(read_global_state(client, app_id))

    app_args = [AppMethods.add]
    call_app(client, private_key, app_id, app_args)
    print(read_global_state(client, app_id))

    app_args = [AppMethods.subtract]
    call_app(client, private_key, app_id, app_args)
    print(read_global_state(client, app_id))

    delete_app(client, private_key, app_id)


if __name__ == "__main__":
    main()
