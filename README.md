# dht-messenger

Простой мессенджер на базе DHT Kademlia

# Приницип работы

Допустим Bob и Alice хотят обмениваться сообщениями:
1. Bob и Alice обмениватся своими публичными ключами pkbob и pkalice
2. Alice хочет отправить перове заширофанное сообщение - она кладет его на адрес `h(pkalice, pkbob)` 
4. Alice добавляет в сообщение адрес ее следующего сообщения. 
5. `Alice 1st message = (key=h(pkalice, pkbob), encrypt(message(text1, next_key=h(key, text1), ts=t1)))`
6. Alice отправляет второе сообщение по сгенерированному адресу 
7. `Alice 2nd message = (key=next_key, encrypt(message(text2, next_key=h(next_key, text2), ts=t2)))`
8. Образуется цепочка сообщений Alice, которую могут читать как Alice так и Bob
9. Bob аналогично пишет сообщения в цепочку, начиная с адреса `h(pkbob, pkalice)` 
10. Для восстановления диалога Alice или Bob сыитвают обе цепочки, начиная с генезисных ключей и мержат по timestamp-ам
