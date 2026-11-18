import auth


def test_hash_acepta_la_clave_correcta_y_rechaza_otra():
    guardado = auth.hashear("secreto")
    assert auth.comprobar("secreto", guardado)
    assert not auth.comprobar("otra", guardado)


def test_la_sal_hace_distintos_los_hashes():
    assert auth.hashear("igual") != auth.hashear("igual")


def test_token_valido():
    datos = auth.verificar_token(auth.crear_token("ana", "admin"))
    assert datos["sub"] == "ana"
    assert datos["rol"] == "admin"
    assert datos["iss"] == "mi-api"


def test_token_vencido_devuelve_none():
    token = auth.crear_token("ana", "admin", minutos=-1)
    assert auth.verificar_token(token) is None


def test_token_alterado_devuelve_none():
    token = auth.crear_token("ana", "lector")
    assert auth.verificar_token(token + "x") is None