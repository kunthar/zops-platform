
# ZOPS Auth, PUSH ve ROC Akışları

## Auth

*   İlk olarak kullanıcı **Zops** üzerinde bir ““account”” oluşturmalıdır. [Signup]([http://zops.io/signup](http://zops.io/signup)) endpoint’ini kullanarak kendinize “account” oluşturabilirsiniz.
*   Mail adresinize gelen linke tıklayarak “account” oluşturmayı kabul edersiniz. Tıklanılan link, sizi kullanıcı bilgilerinizi dolduracağınız bir ekrana yönlendirir.
*   Gerekli alanları doldurduktan sonra ilgili "account"ta tanımlı bir admin hesabı oluşur.
*   Sistem üzerinde işlem yapabilmek için (proje oluşturma, “consumer” oluşturma, "consumer"ları projelere ekleme gibi) geçerli bir token’a sahip olmanız gerekir. Bu tokeni alabilmek için [SAAS loginresource]([https://docs.zops.io/SAAS.html#loginresource](https://docs.zops.io/SAAS.html#loginresource)) adresinden yararlanabilirsiniz.
*   Saas sistemi üzerinden geçerli token aldıktan sonra yapılacak requestlerde bu token kullanılması gerekir.
*   Tokeni request headerinin “AUTHORIZATION” parametre değeri olarak kullanmanız gerekir.(Sistem üzerinde User token olarak bilinen bu tokenin kullanım süresi 1 haftadır. 1 Hafta sonunda geçerliliğini yitirir.)
*   Daha sonra "account"a proje eklemeniz gerekir. Proje eklemek için [project-create–list]([https://docs.zops.io/SAAS.html#project-create--list](https://docs.zops.io/SAAS.html#project-create--list)) adresten yararlanabilirsiniz.
*   Oluşturduğunuz projeye kullanmak istediğiniz servisleri(“roc”, “push) eklemeniz gerekir. Projeye servis eklemek için [service-create]([https://docs.zops.io/SAAS.html#service-create](https://docs.zops.io/SAAS.html#service-create)) ilgili adresten yararlanabilirsiniz.
*   Projelerde kullanmak üzere "account"unuza “consumer” eklemeniz gerekir. Eklenilen "consumer"lar “account” seviyesindedir. “Consumer” eklemek için [consumer-create–list]([https://docs.zops.io/SAAS.html#consumer-create--list](https://docs.zops.io/SAAS.html#consumer-create--list)) adresinden yararlanabilirsiniz.
*   "Account"a eklenen "consumer"ları projenizde kullanabilmek için proje ile "consumer"ı ilişkilendirmeniz gerekir. Siz özel olarak bir projeye ile "consumer"ı ilişkilendirmediğiniz sürece “consumer” projenin servislerini kullanamayacaktır. Proje ile "consumer"i ilişkilendirmek için [consumer-create]([https://docs.zops.io/SAAS.html#project-consumer-create](https://docs.zops.io/SAAS.html#project-consumer-create)) adresinden yararlanabilirsiniz.
*   Daha sonra "consumer"larin proje servislerini kullanabilmesi için token(Saas “consumer” refresh token. Bu tokenin süresi 60sn dir.) üretmeniz gerekir. Bu tokeni hangi service icin alıyorsak request bodysinde ekliyoruz. Aldığımız token belirli bir servis içindir. Bütün servisler için kullanılamaz. Gerekli dökümana [consumer-token-create]([https://docs.zops.io/SAAS.html#consumer-token-create](https://docs.zops.io/SAAS.html#consumer-token-create)) adresinden ulaşabilirsiniz.
*   “Saas” servisinden aldığınız “consumer” refresh token ile “auth” servisine request göndererek refresh token ve access token alıyoruz. Auth servisinden alınan access token servise erişim için kullanılır. Süresi 3 saattir. Acess token ile birlikte gelen refresh tokeni access tokeni yenilemek için kullanabiliriz. Detaylı bilgi için bakınız [AUTH]([https://docs.zops.io/AUTH.html](https://docs.zops.io/AUTH.html)) .

## PUSH

*   Auth servisinden alacağınız push/roc access tokeni ile ilgili servisleri kullanabilirsiniz.
*   Push servisi içerisinde "consumer"lar “user” olarak tanımlıdır. Yazının ilerleyen bölümlerinde ve döküman içerisinde “consumer” “user” olarak anlatılmaktadır.
*   Userların push servisini kullanabilmesi için ilk olarak client register etmeleri gerekir. Client eklenmemiş bir user push sistemi içerisinde tanımlı değildir. Lütfen bu uyarıyı dikkate alınız. Client register etmek için [client-create–list]([https://docs.zops.io/PUSH.html#client-create--list](https://docs.zops.io/PUSH.html#client-create--list)) adresinden yararlanabilirsiniz.
*   Sistem üzerinde user ve clientları gruplandırmak için tag sistemi kullanılmaktadır. Tag tiplerimiz ‘key’, ‘key-value’ ve ‘multi’ dir. Tag değerlerimiz ‘int’, ‘float’ ve ‘str’ dir. Request örneklerini incelemek için [tag-create]([https://docs.zops.io/PUSH.html#tag-create--list](https://docs.zops.io/PUSH.html#tag-create--list)) adresinden yararlanabilirsiniz.
*   Sistem içerisinde oluşturduğumuz taglari ’client’ ile bağdaştırabilirsiniz. Örneğin ‘role’ ismiyle oluşturduğunuz bir ‘multi’, ‘str’ tagı herhangi bir clienta ‘ogrenci’, ‘ogretmen’, ‘memur’ gibi bir değer ile atayabilirsiniz. Örnekler için [client-tag-add–list]([https://docs.zops.io/PUSH.html#client-tag-add--list](https://docs.zops.io/PUSH.html#client-tag-add--list)) adresinden yararlanabilirsiniz.
*   Sistem içerisinde oluşturduğumuz taglari ’user’ ile bağdaştırabilirsiniz. Örneğin ‘sehir’ ismiyle oluşturduğunuz bir ‘multi’, ‘str’ tagı herhangi bir usera ‘izmir’, ‘istanbul’, ‘ankara’ gibi bir değer ile atayabilirsiniz. Örnekler için [client-tag-add–list]([https://docs.zops.io/PUSH.html#client-tag-add--list](https://docs.zops.io/PUSH.html#client-tag-add--list)) adresinden yararlanabilirsiniz.
*   Daha sonra segment oluşturarak mesaj gönderme adımına geçebiliriz. Segmentleri daha önce oluşturduğumuz "tag"ların (user veya client) birleşiminden(`n`), kesişiminden(`U`), farkından(`-`) ve `>, <, =`gibi matematiksel simgeler ile oluşturabilirsiniz. Ayrıntılı bilgi için bakınız [segment-create–create-bulk–list]([https://docs.zops.io/PUSH.html#segment-create--create-bulk--list](https://docs.zops.io/PUSH.html#segment-create--create-bulk--list))
*   Sistemimizden aldığınız segmentId(Mesaj request body “audience” parametresi) sini kullanarak mesaj gönderebiliriz. Mesaj request örneği için [message-post–list]([https://docs.zops.io/PUSH.html#message-post--list](https://docs.zops.io/PUSH.html#message-post--list)) adresinden faydalanabilirsiniz.

## ROC

*   ROC sistemi içerisinde consumerlar kullanıcı(subscriber) olarak tanımlanır.

*   ROC servisini ilk defa kullanacak kullanıcılar için birinci adım “me” endpointi’dir. Bu endpoint aracılığıyla sisteme kendini tanıtır. (_Bu adım işletilmek zorundadır. Lütfen uyarıyı dikkate alınız_). Aynı zamanda bu endpoint’i kullanarak kendisi hakkında bilgi (contacts, channels, bannedChannels, bannedSubscribers, channelInvites, channelJoinRequests, contactRequestsIn, contactRequestsOut) alabilir. Bakınız [me]([%E2%80%98https://gw.zops.io/v1/roc/me'(GET)](https://doc.zops.io/%E2%80%98https://gw.zops.io/v1/roc/me'(GET))) ve [subscriber-retrieval]([https://docs.zops.io/ROC.html#subscriber-retrieval](https://docs.zops.io/ROC.html#subscriber-retrieval))

*   Kişiler arası mesajlaşma için kullanıcıların contact kurmuş olması gerekir. Bunun için contact request göndermemiz veya var olan requesti kabul etmemiz gerekir. İki kullanıcı contact kurduktan sonra mesajlaşabilir.

*   Mesajlaşmak istediğimiz kişiye contact request göndermemiz gerekir. ([https://gw.zops.io/v1/roc/contact-requests]([https://gw.zops.io/v1/roc/contact-requests](https://gw.zops.io/v1/roc/contact-requests)) (POST), [https://docs.zops.io/ROC.html#contact-request-create--list]([https://docs.zops.io/ROC.html#contact-request-create--list](https://docs.zops.io/ROC.html#contact-request-create--list)))

*   Contact request list endpointi ile bize gelen contact requestlerini listeleyebiliriz. ([https://gw.zops.io/v1/roc/contact-requests]([https://gw.zops.io/v1/roc/contact-requests](https://gw.zops.io/v1/roc/contact-requests)) (GET), [https://docs.zops.io/ROC.html#contact-request-create--list]([https://docs.zops.io/ROC.html#contact-request-create--list](https://docs.zops.io/ROC.html#contact-request-create--list)))

*   Listelediğimiz contact requestlerini kabul etmek veya reddetmek için ([https://gw.zops.io/v1/roc/contact-requests/{invite_id}]([https://gw.zops.io/v1/roc/contact-requests/%7Binvite_id%7D](https://gw.zops.io/v1/roc/contact-requests/%7Binvite_id%7D)) (PUT), [https://docs.zops.io/ROC.html#contact-request-accept--reject]([https://docs.zops.io/ROC.html#contact-request-accept--reject](https://docs.zops.io/ROC.html#contact-request-accept--reject)))

*   Contact listemizde olan bir kişiye mesaj atabilmek için ([https://gw.zops.io/v1/roc/messages/]([https://gw.zops.io/v1/roc/messages/](https://gw.zops.io/v1/roc/messages/)) (POST), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))

*   Bir kullanıcıdan gelen mesajlara ulaşabilmek için ([https://gw.zops.io/v1/roc/messages?subscriber={{subscriberId}]([https://gw.zops.io/v1/roc/messages?subscriber=%7B%7BsubscriberId%7D](https://gw.zops.io/v1/roc/messages?subscriber=%7B%7BsubscriberId%7D))} (GET), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))

Grup mesajlaşması için;

*   Kanal oluşturmak için ([https://gw.zops.io/v1/roc/channels]([https://gw.zops.io/v1/roc/channels](https://gw.zops.io/v1/roc/channels)) (POST), [https://docs.zops.io/ROC.html#channel-list--create]([https://docs.zops.io/ROC.html#channel-list--create](https://docs.zops.io/ROC.html#channel-list--create)))
*   Kullanıcıyı kanala davet etmek veya kanala katılma talebi göndermek için ([https://gw.zops.io/v1/roc/invites]([https://gw.zops.io/v1/roc/invites](https://gw.zops.io/v1/roc/invites)) (POST), [https://docs.zops.io/ROC.html#invitation-create]([https://docs.zops.io/ROC.html#invitation-create](https://docs.zops.io/ROC.html#invitation-create)))
*   Yetkili olarak kanala gelen katılma taleplerini kabul etmek - reddetmek için ([https://gw.zops.io/v1/roc/invites/{{joinRequestId}]([https://gw.zops.io/v1/roc/invites/%7B%7BjoinRequestId%7D](https://gw.zops.io/v1/roc/invites/%7B%7BjoinRequestId%7D))} (PUT), [https://docs.zops.io/ROC.html#invitation-accept--reject--cancel]([https://docs.zops.io/ROC.html#invitation-accept--reject--cancel](https://docs.zops.io/ROC.html#invitation-accept--reject--cancel)))
*   Kanaldan gelen daveti kabul etmek - reddetmek için ([https://gw.zops.io/v1/roc/invites/{{inviteId}]([https://gw.zops.io/v1/roc/invites/%7B%7BinviteId%7D](https://gw.zops.io/v1/roc/invites/%7B%7BinviteId%7D))} (PUT), [https://docs.zops.io/ROC.html#invitation-accept--reject--cancel]([https://docs.zops.io/ROC.html#invitation-accept--reject--cancel](https://docs.zops.io/ROC.html#invitation-accept--reject--cancel)))
*   Kanala mesaj göndermek için ([https://gw.zops.io/v1/roc/messages]([https://gw.zops.io/v1/roc/messages](https://gw.zops.io/v1/roc/messages)) (POST), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))
*   Kanal mesajlarını listelemek için ([https://gw.zops.io/v1/roc/messages?channel={{channelId}]([https://gw.zops.io/v1/roc/messages?channel=%7B%7BchannelId%7D](https://gw.zops.io/v1/roc/messages?channel=%7B%7BchannelId%7D))} (GET), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))

Burda yazan işlemler birebir mesajlaşma ve kanal mesajlaşması için uygulanması gereken en temel özelliklerdir. Bahsedilen kullanıcılar arası mesajlaşma ve kanal mesajlaşması adımları postman collection olarak eklenecektir.

Ek olarak;

*   Kullanıcının durumunu(status) almak ve değiştirmek için ([https://gw.zops.io/v1/roc/status]([https://gw.zops.io/v1/roc/status](https://gw.zops.io/v1/roc/status)) (GET, POST), [https://docs.zops.io/ROC.html#sending-and-retrieving-status]([https://docs.zops.io/ROC.html#sending-and-retrieving-status](https://docs.zops.io/ROC.html#sending-and-retrieving-status)))
*   Kanal bilgilerini alabilmek, kanalı güncelleyebilmek silebilmek için ([https://gw.zops.io/v1/roc/channels/{{channelId}]([https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D](https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D))} (GET, PUT, DELETE), [https://docs.zops.io/ROC.html#channel-update--delete--retrieve]([https://docs.zops.io/ROC.html#channel-update--delete--retrieve](https://docs.zops.io/ROC.html#channel-update--delete--retrieve)))
*   Yetkili olarak bir kullanıcıyı kanaldan çıkarmak veya kanal üyesi olarak kanaldan çıkmak için ([https://gw.zops.io/v1/roc/channels/{{channelId}]([https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D](https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D))}/subscribers/{{subscriberId}} (DELETE), [https://docs.zops.io/ROC.html#unsubscribe-from-a-channel-or-unsubscribe-a-subscriber-from-a-channel]([https://docs.zops.io/ROC.html#unsubscribe-from-a-channel-or-unsubscribe-a-subscriber-from-a-channel](https://docs.zops.io/ROC.html#unsubscribe-from-a-channel-or-unsubscribe-a-subscriber-from-a-channel)))
*   Bir kullanıcı olarak kanalı banlamak için veya kanal yetkilisi olarak bir kullanıcı banlamak için ([https://gw.zops.io/v1/roc/banned-channels]([https://gw.zops.io/v1/roc/banned-channels](https://gw.zops.io/v1/roc/banned-channels)) (POST), [https://docs.zops.io/ROC.html#ban-channel-subscriber]([https://docs.zops.io/ROC.html#ban-channel-subscriber](https://docs.zops.io/ROC.html#ban-channel-subscriber)))
*   Kullanıcı silmek için ([https://gw.zops.io/v1/roc/contacts/{{subscriberId}]([https://gw.zops.io/v1/roc/contacts/%7B%7BsubscriberId%7D](https://gw.zops.io/v1/roc/contacts/%7B%7BsubscriberId%7D))} (DELETE), [https://docs.zops.io/ROC.html#contact-delete]([https://docs.zops.io/ROC.html#contact-delete](https://docs.zops.io/ROC.html#contact-delete)))
*   Kullanıcı banlamak için ([https://gw.zops.io/v1/roc/banned-contacts]([https://gw.zops.io/v1/roc/banned-contacts](https://gw.zops.io/v1/roc/banned-contacts)) (POST), [https://docs.zops.io/ROC.html#ban-subscriber]([https://docs.zops.io/ROC.html#ban-subscriber](https://docs.zops.io/ROC.html#ban-subscriber)))  
    işlemleri yapılabilir.

Admin Roc Kanal Yaratma ve Güncelleme İşlemi İçin;

*   Öncelikle projemize ait admin service tokenini almamiz gerekmektedir. Bu tokeni https://saas.zops.io/api/v1/projects/{{projectId}}/services-token] (GET) adresinden alabilirsiniz. Bu token için expire suresi yoktur. Proje başına sadece bir adet yaratılabilir. Yenisini aldığınızda daha önce var olan token invalid hale getirilir.
*   Daha sonra bu token ile roc servisinden kanal yaratabilirsiniz.Aşağıda örnek bir request bulunmaktadır. ([https://gw.zops.io/v1/roc/admin/create-channel]([https://gw.zops.io/v1/roc/admin/create-channel](https://gw.zops.io/v1/roc/banned-contacts)) (POST) 
```curl
curl -X POST \ https://gw.zops.io/v1/roc/admin/create-channel \ -H 'AUTHORIZATION: Token AdminToken’ \ -H 'Content-Type: application/json' \ -d '{ "name": "Test Admin Create Private Channel 1", "description": "Test Admin Create Private Channel Description", "channelType": "private", "subscribers": ["2e06406da329463d8a6c4dc31c0d864d", "d467b353b23c4e14a97df6dcd75a1b0a", "a75c7be7d2f14c3a8c91615ba2b0b80c", "475947b057ee45288e8a57946ab43bb6"], "managers": ["2e06406da329463d8a6c4dc31c0d864d"] }'
```
*   Roc sisteminde tanımlı olan bir kanalı admin kullanıcı olarak güncelleyebilirsiniz. https://gw.zops.io/v1/roc/admin/channels/{{channel_id}} (PUT)
```curl
PUT /v1/roc/admin/channels/63958c8642fc4cb7971ea0ea49cf08f4 HTTP/1.1
Host: https://gw.zops.io
Content-Type: application/json
AUTHORIZATION: Token wL8e00g7vL8RKHoxZSA_VOH7VXZXy02gA2Qg8oVLHIDdQ-orDWQIvNggKyCLHLAUm-NQT74jQF4MEEjpAYABsQ
{
	"name": "Test Admin Update Private Channel 1", 
	"description": "Test Admin Update Private Channel Description", 
	"channelType": "private",
	"subscribers": ["cdb20149dfe249b192bd07bd36280ebd"],
	"managers": ["4e9593e3a0a84a58877048bb3b7c926c"]
}
```

Belirli bir kullanıcıya yeni contact eklemek için;

*   Öncelikle projemize ait admin service tokenini almamiz gerekmektedir. Bu tokeni https://saas.zops.io/api/v1/projects/{{projectId}}/services-token] (GET) adresinden alabilirsiniz. Bu token için expire suresi yoktur. Proje başına sadece bir adet yaratılabilir. Yenisini aldığınızda daha önce var olan token invalid hale getirilir.
* Belirli bir kullanıcıya (subscriber) yeni contact listesi eklemek için https://gw.zops.io/v1/roc/admin/contact (POST) endpointini kullanabilirsiniz. "subscriber_id" parametresi yeni contact eklenecek kullanıcıyı temsil eder.
"contactListToAdd" parametresi ROC sisteminde tanımlı olan kullanıcıların (subscriber) id'lerinden oluşan bir listedir. Bu parametreye contact olarak eklenecek kişileri liste olarak geçmeniz gerekmektedir.
Aşağıda örnek bir request paylaşılmıştır. 
```curl
POST /v1/roc/admin/contact HTTP/1.1
Host: https://gw.zops.io
Content-Type: application/json
AUTHORIZATION: Token wL8e00g7vL8RKHoxZSA_VOH7VXZXy02gA2Qg8oVLHIDdQ-orDWQIvNggKyCLHLAUm-NQT74jQF4MEEjpAYABsQ
{
	"subscriber_id": "4e9593e3a0a84a58877048bb3b7c926c", 
	"contactListToAdd": ["4e9593e3a0a84a58877048bb3b7c926c","cdb20149dfe249b192bd07bd36280ebd", "5bf760d7e783479792666f239a27c8e9", "c30668463ca5437b8665dbdd660d65ec"]
}
```

# ZOPS Auth, PUSH ve ROC Akışları

## Auth

*   İlk olarak kullanıcı **Zops** üzerinde bir ““account”” oluşturmalıdır. [Signup]([http://zops.io/signup](http://zops.io/signup)) endpoint’ini kullanarak kendinize “account” oluşturabilirsiniz.
*   Mail adresinize gelen linke tıklayarak “account” oluşturmayı kabul edersiniz. Tıklanılan link, sizi kullanıcı bilgilerinizi dolduracağınız bir ekrana yönlendirir.
*   Gerekli alanları doldurduktan sonra ilgili "account"ta tanımlı bir admin hesabı oluşur.
*   Sistem üzerinde işlem yapabilmek için (proje oluşturma, “consumer” oluşturma, "consumer"ları projelere ekleme gibi) geçerli bir token’a sahip olmanız gerekir. Bu tokeni alabilmek için [SAAS loginresource]([https://docs.zops.io/SAAS.html#loginresource](https://docs.zops.io/SAAS.html#loginresource)) adresinden yararlanabilirsiniz.
*   Saas sistemi üzerinden geçerli token aldıktan sonra yapılacak requestlerde bu token kullanılması gerekir.
*   Tokeni request headerinin “AUTHORIZATION” parametre değeri olarak kullanmanız gerekir.(Sistem üzerinde User token olarak bilinen bu tokenin kullanım süresi 1 haftadır. 1 Hafta sonunda geçerliliğini yitirir.)
*   Daha sonra "account"a proje eklemeniz gerekir. Proje eklemek için [project-create–list]([https://docs.zops.io/SAAS.html#project-create--list](https://docs.zops.io/SAAS.html#project-create--list)) adresten yararlanabilirsiniz.
*   Oluşturduğunuz projeye kullanmak istediğiniz servisleri(“roc”, “push) eklemeniz gerekir. Projeye servis eklemek için [service-create]([https://docs.zops.io/SAAS.html#service-create](https://docs.zops.io/SAAS.html#service-create)) ilgili adresten yararlanabilirsiniz.
*   Projelerde kullanmak üzere "account"unuza “consumer” eklemeniz gerekir. Eklenilen "consumer"lar “account” seviyesindedir. “Consumer” eklemek için [consumer-create–list]([https://docs.zops.io/SAAS.html#consumer-create--list](https://docs.zops.io/SAAS.html#consumer-create--list)) adresinden yararlanabilirsiniz.
*   "Account"a eklenen "consumer"ları projenizde kullanabilmek için proje ile "consumer"ı ilişkilendirmeniz gerekir. Siz özel olarak bir projeye ile "consumer"ı ilişkilendirmediğiniz sürece “consumer” projenin servislerini kullanamayacaktır. Proje ile "consumer"i ilişkilendirmek için [consumer-create]([https://docs.zops.io/SAAS.html#project-consumer-create](https://docs.zops.io/SAAS.html#project-consumer-create)) adresinden yararlanabilirsiniz.
*   Daha sonra "consumer"larin proje servislerini kullanabilmesi için token(Saas “consumer” refresh token. Bu tokenin süresi 60sn dir.) üretmeniz gerekir. Bu tokeni hangi service icin alıyorsak request bodysinde ekliyoruz. Aldığımız token belirli bir servis içindir. Bütün servisler için kullanılamaz. Gerekli dökümana [consumer-token-create]([https://docs.zops.io/SAAS.html#consumer-token-create](https://docs.zops.io/SAAS.html#consumer-token-create)) adresinden ulaşabilirsiniz.
*   “Saas” servisinden aldığınız “consumer” refresh token ile “auth” servisine request göndererek refresh token ve access token alıyoruz. Auth servisinden alınan access token servise erişim için kullanılır. Süresi 3 saattir. Acess token ile birlikte gelen refresh tokeni access tokeni yenilemek için kullanabiliriz. Detaylı bilgi için bakınız [AUTH]([https://docs.zops.io/AUTH.html](https://docs.zops.io/AUTH.html)) .

## PUSH

*   Auth servisinden alacağınız push/roc access tokeni ile ilgili servisleri kullanabilirsiniz.
*   Push servisi içerisinde "consumer"lar “user” olarak tanımlıdır. Yazının ilerleyen bölümlerinde ve döküman içerisinde “consumer” “user” olarak anlatılmaktadır.
*   Userların push servisini kullanabilmesi için ilk olarak client register etmeleri gerekir. Client eklenmemiş bir user push sistemi içerisinde tanımlı değildir. Lütfen bu uyarıyı dikkate alınız. Client register etmek için [client-create–list]([https://docs.zops.io/PUSH.html#client-create--list](https://docs.zops.io/PUSH.html#client-create--list)) adresinden yararlanabilirsiniz.
*   Sistem üzerinde user ve clientları gruplandırmak için tag sistemi kullanılmaktadır. Tag tiplerimiz ‘key’, ‘key-value’ ve ‘multi’ dir. Tag değerlerimiz ‘int’, ‘float’ ve ‘str’ dir. Request örneklerini incelemek için [tag-create]([https://docs.zops.io/PUSH.html#tag-create--list](https://docs.zops.io/PUSH.html#tag-create--list)) adresinden yararlanabilirsiniz.
*   Sistem içerisinde oluşturduğumuz taglari ’client’ ile bağdaştırabilirsiniz. Örneğin ‘role’ ismiyle oluşturduğunuz bir ‘multi’, ‘str’ tagı herhangi bir clienta ‘ogrenci’, ‘ogretmen’, ‘memur’ gibi bir değer ile atayabilirsiniz. Örnekler için [client-tag-add–list]([https://docs.zops.io/PUSH.html#client-tag-add--list](https://docs.zops.io/PUSH.html#client-tag-add--list)) adresinden yararlanabilirsiniz.
*   Sistem içerisinde oluşturduğumuz taglari ’user’ ile bağdaştırabilirsiniz. Örneğin ‘sehir’ ismiyle oluşturduğunuz bir ‘multi’, ‘str’ tagı herhangi bir usera ‘izmir’, ‘istanbul’, ‘ankara’ gibi bir değer ile atayabilirsiniz. Örnekler için [client-tag-add–list]([https://docs.zops.io/PUSH.html#client-tag-add--list](https://docs.zops.io/PUSH.html#client-tag-add--list)) adresinden yararlanabilirsiniz.
*   Daha sonra segment oluşturarak mesaj gönderme adımına geçebiliriz. Segmentleri daha önce oluşturduğumuz "tag"ların (user veya client) birleşiminden(`n`), kesişiminden(`U`), farkından(`-`) ve `>, <, =`gibi matematiksel simgeler ile oluşturabilirsiniz. Ayrıntılı bilgi için bakınız [segment-create–create-bulk–list]([https://docs.zops.io/PUSH.html#segment-create--create-bulk--list](https://docs.zops.io/PUSH.html#segment-create--create-bulk--list))
*   Sistemimizden aldığınız segmentId(Mesaj request body “audience” parametresi) sini kullanarak mesaj gönderebiliriz. Mesaj request örneği için [message-post–list]([https://docs.zops.io/PUSH.html#message-post--list](https://docs.zops.io/PUSH.html#message-post--list)) adresinden faydalanabilirsiniz.

## ROC

*   ROC sistemi içerisinde consumerlar kullanıcı(subscriber) olarak tanımlanır.

*   ROC servisini ilk defa kullanacak kullanıcılar için birinci adım “me” endpointi’dir. Bu endpoint aracılığıyla sisteme kendini tanıtır. (_Bu adım işletilmek zorundadır. Lütfen uyarıyı dikkate alınız_). Aynı zamanda bu endpoint’i kullanarak kendisi hakkında bilgi (contacts, channels, bannedChannels, bannedSubscribers, channelInvites, channelJoinRequests, contactRequestsIn, contactRequestsOut) alabilir. Bakınız [me]([%E2%80%98https://gw.zops.io/v1/roc/me'(GET)](https://doc.zops.io/%E2%80%98https://gw.zops.io/v1/roc/me'(GET))) ve [subscriber-retrieval]([https://docs.zops.io/ROC.html#subscriber-retrieval](https://docs.zops.io/ROC.html#subscriber-retrieval))

*   Kişiler arası mesajlaşma için kullanıcıların contact kurmuş olması gerekir. Bunun için contact request göndermemiz veya var olan requesti kabul etmemiz gerekir. İki kullanıcı contact kurduktan sonra mesajlaşabilir.

*   Mesajlaşmak istediğimiz kişiye contact request göndermemiz gerekir. ([https://gw.zops.io/v1/roc/contact-requests]([https://gw.zops.io/v1/roc/contact-requests](https://gw.zops.io/v1/roc/contact-requests)) (POST), [https://docs.zops.io/ROC.html#contact-request-create--list]([https://docs.zops.io/ROC.html#contact-request-create--list](https://docs.zops.io/ROC.html#contact-request-create--list)))

*   Contact request list endpointi ile bize gelen contact requestlerini listeleyebiliriz. ([https://gw.zops.io/v1/roc/contact-requests]([https://gw.zops.io/v1/roc/contact-requests](https://gw.zops.io/v1/roc/contact-requests)) (GET), [https://docs.zops.io/ROC.html#contact-request-create--list]([https://docs.zops.io/ROC.html#contact-request-create--list](https://docs.zops.io/ROC.html#contact-request-create--list)))

*   Listelediğimiz contact requestlerini kabul etmek veya reddetmek için ([https://gw.zops.io/v1/roc/contact-requests/{invite_id}]([https://gw.zops.io/v1/roc/contact-requests/%7Binvite_id%7D](https://gw.zops.io/v1/roc/contact-requests/%7Binvite_id%7D)) (PUT), [https://docs.zops.io/ROC.html#contact-request-accept--reject]([https://docs.zops.io/ROC.html#contact-request-accept--reject](https://docs.zops.io/ROC.html#contact-request-accept--reject)))

*   Contact listemizde olan bir kişiye mesaj atabilmek için ([https://gw.zops.io/v1/roc/messages/]([https://gw.zops.io/v1/roc/messages/](https://gw.zops.io/v1/roc/messages/)) (POST), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))

*   Bir kullanıcıdan gelen mesajlara ulaşabilmek için ([https://gw.zops.io/v1/roc/messages?subscriber={{subscriberId}]([https://gw.zops.io/v1/roc/messages?subscriber=%7B%7BsubscriberId%7D](https://gw.zops.io/v1/roc/messages?subscriber=%7B%7BsubscriberId%7D))} (GET), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))

Grup mesajlaşması için;

*   Kanal oluşturmak için ([https://gw.zops.io/v1/roc/channels]([https://gw.zops.io/v1/roc/channels](https://gw.zops.io/v1/roc/channels)) (POST), [https://docs.zops.io/ROC.html#channel-list--create]([https://docs.zops.io/ROC.html#channel-list--create](https://docs.zops.io/ROC.html#channel-list--create)))
*   Kullanıcıyı kanala davet etmek veya kanala katılma talebi göndermek için ([https://gw.zops.io/v1/roc/invites]([https://gw.zops.io/v1/roc/invites](https://gw.zops.io/v1/roc/invites)) (POST), [https://docs.zops.io/ROC.html#invitation-create]([https://docs.zops.io/ROC.html#invitation-create](https://docs.zops.io/ROC.html#invitation-create)))
*   Yetkili olarak kanala gelen katılma taleplerini kabul etmek - reddetmek için ([https://gw.zops.io/v1/roc/invites/{{joinRequestId}]([https://gw.zops.io/v1/roc/invites/%7B%7BjoinRequestId%7D](https://gw.zops.io/v1/roc/invites/%7B%7BjoinRequestId%7D))} (PUT), [https://docs.zops.io/ROC.html#invitation-accept--reject--cancel]([https://docs.zops.io/ROC.html#invitation-accept--reject--cancel](https://docs.zops.io/ROC.html#invitation-accept--reject--cancel)))
*   Kanaldan gelen daveti kabul etmek - reddetmek için ([https://gw.zops.io/v1/roc/invites/{{inviteId}]([https://gw.zops.io/v1/roc/invites/%7B%7BinviteId%7D](https://gw.zops.io/v1/roc/invites/%7B%7BinviteId%7D))} (PUT), [https://docs.zops.io/ROC.html#invitation-accept--reject--cancel]([https://docs.zops.io/ROC.html#invitation-accept--reject--cancel](https://docs.zops.io/ROC.html#invitation-accept--reject--cancel)))
*   Kanala mesaj göndermek için ([https://gw.zops.io/v1/roc/messages]([https://gw.zops.io/v1/roc/messages](https://gw.zops.io/v1/roc/messages)) (POST), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))
*   Kanal mesajlarını listelemek için ([https://gw.zops.io/v1/roc/messages?channel={{channelId}]([https://gw.zops.io/v1/roc/messages?channel=%7B%7BchannelId%7D](https://gw.zops.io/v1/roc/messages?channel=%7B%7BchannelId%7D))} (GET), [https://docs.zops.io/ROC.html#message-create--list]([https://docs.zops.io/ROC.html#message-create--list](https://docs.zops.io/ROC.html#message-create--list)))

Burda yazan işlemler birebir mesajlaşma ve kanal mesajlaşması için uygulanması gereken en temel özelliklerdir. Bahsedilen kullanıcılar arası mesajlaşma ve kanal mesajlaşması adımları postman collection olarak eklenecektir.

Ek olarak;

*   Kullanıcının durumunu(status) almak ve değiştirmek için ([https://gw.zops.io/v1/roc/status]([https://gw.zops.io/v1/roc/status](https://gw.zops.io/v1/roc/status)) (GET, POST), [https://docs.zops.io/ROC.html#sending-and-retrieving-status]([https://docs.zops.io/ROC.html#sending-and-retrieving-status](https://docs.zops.io/ROC.html#sending-and-retrieving-status)))
*   Kanal bilgilerini alabilmek, kanalı güncelleyebilmek silebilmek için ([https://gw.zops.io/v1/roc/channels/{{channelId}]([https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D](https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D))} (GET, PUT, DELETE), [https://docs.zops.io/ROC.html#channel-update--delete--retrieve]([https://docs.zops.io/ROC.html#channel-update--delete--retrieve](https://docs.zops.io/ROC.html#channel-update--delete--retrieve)))
*   Yetkili olarak bir kullanıcıyı kanaldan çıkarmak veya kanal üyesi olarak kanaldan çıkmak için ([https://gw.zops.io/v1/roc/channels/{{channelId}]([https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D](https://gw.zops.io/v1/roc/channels/%7B%7BchannelId%7D))}/subscribers/{{subscriberId}} (DELETE), [https://docs.zops.io/ROC.html#unsubscribe-from-a-channel-or-unsubscribe-a-subscriber-from-a-channel]([https://docs.zops.io/ROC.html#unsubscribe-from-a-channel-or-unsubscribe-a-subscriber-from-a-channel](https://docs.zops.io/ROC.html#unsubscribe-from-a-channel-or-unsubscribe-a-subscriber-from-a-channel)))
*   Bir kullanıcı olarak kanalı banlamak için veya kanal yetkilisi olarak bir kullanıcı banlamak için ([https://gw.zops.io/v1/roc/banned-channels]([https://gw.zops.io/v1/roc/banned-channels](https://gw.zops.io/v1/roc/banned-channels)) (POST), [https://docs.zops.io/ROC.html#ban-channel-subscriber]([https://docs.zops.io/ROC.html#ban-channel-subscriber](https://docs.zops.io/ROC.html#ban-channel-subscriber)))
*   Kullanıcı silmek için ([https://gw.zops.io/v1/roc/contacts/{{subscriberId}]([https://gw.zops.io/v1/roc/contacts/%7B%7BsubscriberId%7D](https://gw.zops.io/v1/roc/contacts/%7B%7BsubscriberId%7D))} (DELETE), [https://docs.zops.io/ROC.html#contact-delete]([https://docs.zops.io/ROC.html#contact-delete](https://docs.zops.io/ROC.html#contact-delete)))
*   Kullanıcı banlamak için ([https://gw.zops.io/v1/roc/banned-contacts]([https://gw.zops.io/v1/roc/banned-contacts](https://gw.zops.io/v1/roc/banned-contacts)) (POST), [https://docs.zops.io/ROC.html#ban-subscriber]([https://docs.zops.io/ROC.html#ban-subscriber](https://docs.zops.io/ROC.html#ban-subscriber)))  
    işlemleri yapılabilir.

Admin Roc Kanal Yaratma ve Güncelleme İşlemi İçin;

*   Öncelikle projeye ait admin service tokenının alınması gerekmektedir. Bu tokeni https://saas.zops.io/api/v1/projects/{{projectId}}/services-token] (GET) adresinden alabilirsiniz. Bu token için expire suresi yoktur. Proje başına sadece bir adet yaratılabilir. Yenisini aldığınızda daha önce var olan token invalid hale getirilir.
*   Daha sonra bu token ile roc servisinden kanal yaratabilirsiniz.Aşağıda örnek bir request bulunmaktadır. ([https://gw.zops.io/v1/roc/admin/create-channel]([https://gw.zops.io/v1/roc/admin/create-channel](https://gw.zops.io/v1/roc/banned-contacts)) (POST) 
```curl
curl -X POST \ https://gw.zops.io/v1/roc/admin/create-channel \ -H 'AUTHORIZATION: Token AdminToken’ \ -H 'Content-Type: application/json' \ -d '{ "name": "Test Admin Create Private Channel 1", "description": "Test Admin Create Private Channel Description", "channelType": "private", "subscribers": ["2e06406da329463d8a6c4dc31c0d864d", "d467b353b23c4e14a97df6dcd75a1b0a", "a75c7be7d2f14c3a8c91615ba2b0b80c", "475947b057ee45288e8a57946ab43bb6"], "managers": ["2e06406da329463d8a6c4dc31c0d864d"] }'
```
*   Roc sisteminde tanımlı olan bir kanalı admin kullanıcı olarak güncelleyebilirsiniz. https://gw.zops.io/v1/roc/admin/channels/{{channel_id}} (PUT)
```
PUT /v1/roc/admin/channels/63958c8642fc4cb7971ea0ea49cf08f4 HTTP/1.1
Host: https://gw.zops.io
Content-Type: application/json
AUTHORIZATION: Token wL8e00g7vL8RKHoxZSA_VOH7VXZXy02gA2Qg8oVLHIDdQ-orDWQIvNggKyCLHLAUm-NQT74jQF4MEEjpAYABsQ
{
	"name": "Test Admin Update Private Channel 1", 
	"description": "Test Admin Update Private Channel Description", 
	"channelType": "private",
	"subscribers": ["cdb20149dfe249b192bd07bd36280ebd"],
	"managers": ["4e9593e3a0a84a58877048bb3b7c926c"]
}
```

Belirli bir kullanıcıya yeni contact eklemek için;

*   Öncelikle projeye ait admin service tokenının alınması gerekmektedir. Bu tokeni https://saas.zops.io/api/v1/projects/{{projectId}}/services-token] (GET) adresinden alabilirsiniz. Bu token için expire suresi yoktur. Proje başına sadece bir adet yaratılabilir. Yenisini aldığınızda daha önce var olan token invalid hale getirilir.
* Belirli bir kullanıcıya (subscriber) yeni contact listesi eklemek için https://gw.zops.io/v1/roc/admin/contact (POST) endpointini kullanabilirsiniz. "subscriber_id" parametresi yeni contact eklenecek kullanıcıyı temsil eder.
"contactListToAdd" parametresi ROC sisteminde tanımlı olan kullanıcıların (subscriber) id'lerinden oluşan bir listedir. Bu parametreye contact olarak eklenecek kişileri liste olarak geçmeniz gerekmektedir.
Aşağıda örnek bir request paylaşılmıştır. 
```
POST /v1/roc/admin/contact HTTP/1.1
Host: https://gw.zops.io
Content-Type: application/json
AUTHORIZATION: Token wL8e00g7vL8RKHoxZSA_VOH7VXZXy02gA2Qg8oVLHIDdQ-orDWQIvNggKyCLHLAUm-NQT74jQF4MEEjpAYABsQ
{
	"subscriber_id": "4e9593e3a0a84a58877048bb3b7c926c", 
	"contactListToAdd": ["4e9593e3a0a84a58877048bb3b7c926c","cdb20149dfe249b192bd07bd36280ebd", "5bf760d7e783479792666f239a27c8e9", "c30668463ca5437b8665dbdd660d65ec"]
}
```
