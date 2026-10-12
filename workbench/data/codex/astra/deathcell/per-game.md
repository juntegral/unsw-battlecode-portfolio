# 판별 반복 사망 [M]

[M] 머리의 마지막 유효 좌표를 사망 칸으로 센다. 벽 충돌 시도 도착 칸은 별개다. 적 머리에서 그 칸까지 실제 벽·포털을 반영한 최단 경로가 3걸음 이내이면 제외한다. 몸은 거리 계산에서 무시한다.

[M] 비전투 분모=벽/자기몸/아군몸/아군머리/무행동. 비전투가 지형 탓이라는 뜻은 아니다. lost는 사망 직전 길이 합이며 낙하 재섭취를 빼지 않은 총량이다.

[M] 세부 칸/라운드/각 L/여왕/포털 진입/진주: [cells.csv](cells.csv), [cells.jsonl](cells.jsonl). 각 death record의 component_entrance는 열린 변 성분에 들어온 사건이고 last_step은 사망 칸의 마지막 진입이다. 초기 배치/출생으로 들어온 경우는 별도로 표기한다.

|[M] 판|버전|지도|상대|우리 반복 칸/사망/총 L/Q|우리 비전투 분모|상대 반복 칸/사망/총 L/Q|상대 비전투 분모|
|---|---|---|---|---:|---:|---:|---:|
|1461128|one1|weakhold|dev test 1 :P|2/34/68/0|51|0/0/0/0|11|
|1461129|one1|Australia|dev test 1 :P|0/0/0/0|4|27/141/425/0|229|
|1461130|one1|Islands|dev test 1 :P|15/74/173/0|146|3/7/28/0|321|
|1461131|one1|Maze|dev test 1 :P|50/219/496/1|445|0/0/0/0|450|
|1461132|one1|Stripes|dev test 1 :P|1/6/12/1|6|0/0/0/0|38|
|1461133|one1|Tower Defense|dev test 1 :P|0/0/0/0|4|0/0/0/0|8|
|1461134|one1|Around UNSW|dev test 1 :P|23/105/235/0|285|65/348/1077/0|509|
|1461135|one1|Default|dev test 1 :P|1/2/4/0|5|3/7/17/0|158|
|1461136|one1|Queen Of Spades|dev test 1 :P|4/22/50/0|34|3/6/13/0|76|
|1461137|one1|Schooltime|dev test 1 :P|2/4/10/0|13|0/0/0/0|187|
|1461138|one1|Trophy|dev test 1 :P|0/0/0/0|0|0/0/0/0|6|
|1461139|one1|Devil|dev test 1 :P|6/17/38/1|24|76/373/828/0|444|
|1461140|one1|Trauma|dev test 1 :P|5/31/63/0|69|2/6/17/0|249|
|1461141|one1|Portals|dev test 1 :P|47/447/1139/1|516|7/23/50/0|574|
|1461142|one1|Slithery Fight|dev test 1 :P|61/296/707/0|555|2/4/11/0|1081|
|1460555|one1|weakhold|WeHaveQuizzes|26/159/348/0|212|13/183/374/0|234|
|1460556|one1|Australia|WeHaveQuizzes|22/133/316/0|208|13/44/150/0|192|
|1460557|one1|Islands|WeHaveQuizzes|23/78/182/0|244|14/60/137/0|207|
|1460558|one1|Maze|WeHaveQuizzes|57/213/502/0|454|21/131/277/0|451|
|1460559|one1|Stripes|WeHaveQuizzes|0/0/0/0|0|3/14/28/0|20|
|1460560|one1|Tower Defense|WeHaveQuizzes|1/2/4/0|5|0/0/0/0|9|
|1460561|one1|Around UNSW|WeHaveQuizzes|12/72/161/0|250|33/145/443/0|368|
|1460562|one1|Default|WeHaveQuizzes|1/2/5/0|24|4/10/24/0|97|
|1460563|one1|Queen Of Spades|WeHaveQuizzes|0/0/0/0|0|8/32/82/0|95|
|1460564|one1|Schooltime|WeHaveQuizzes|84/283/670/0|434|38/94/252/0|425|
|1460565|one1|Trophy|WeHaveQuizzes|2/7/17/0|22|0/0/0/0|0|
|1460566|one1|Devil|WeHaveQuizzes|72/265/629/0|329|1/2/4/0|14|
|1460567|one1|Trauma|WeHaveQuizzes|8/54/114/0|86|24/120/260/0|332|
|1460568|one1|Portals|WeHaveQuizzes|50/474/1196/1|554|28/259/638/0|461|
|1460569|one1|Slithery Fight|WeHaveQuizzes|73/351/832/0|545|69/404/962/0|918|
|1462980|one2|weakhold|WeHaveQuizzes|5/80/168/0|103|23/240/504/0|391|
|1462981|one2|Australia|WeHaveQuizzes|11/49/111/0|128|13/51/135/0|237|
|1462982|one2|Islands|WeHaveQuizzes|27/105/246/0|267|14/64/144/0|198|
|1462983|one2|Maze|WeHaveQuizzes|34/143/318/0|286|38/195/412/0|507|
|1462984|one2|Stripes|WeHaveQuizzes|10/53/116/1|65|6/33/74/0|41|
|1462985|one2|Tower Defense|WeHaveQuizzes|0/0/0/0|1|0/0/0/0|14|
|1462986|one2|Around UNSW|WeHaveQuizzes|18/113/244/0|293|30/111/332/0|325|
|1462987|one2|Default|WeHaveQuizzes|5/10/25/0|38|0/0/0/0|14|
|1462988|one2|Queen Of Spades|WeHaveQuizzes|8/38/93/0|48|5/26/64/0|75|
|1462989|one2|Schooltime|WeHaveQuizzes|25/86/197/0|242|50/124/298/0|548|
|1462990|one2|Trophy|WeHaveQuizzes|0/0/0/0|1|2/5/10/0|23|
|1462991|one2|Devil|WeHaveQuizzes|0/0/0/0|0|1/2/4/0|12|
|1462992|one2|Trauma|WeHaveQuizzes|16/78/165/0|131|17/101/207/0|302|
|1462993|one2|Portals|WeHaveQuizzes|51/470/1215/1|559|26/224/548/1|371|
|1462994|one2|Slithery Fight|WeHaveQuizzes|61/591/1310/0|861|61/472/1070/0|954|
|1465965|one3|weakhold|dev test 1 :P|6/67/142/1|82|0/0/0/0|202|
|1465966|one3|Australia|dev test 1 :P|6/36/80/0|42|43/117/498/0|265|
|1465967|one3|Islands|dev test 1 :P|30/135/300/0|228|5/13/49/0|274|
|1465968|one3|Maze|dev test 1 :P|65/235/572/0|440|0/0/0/0|331|
|1465969|one3|Stripes|dev test 1 :P|0/0/0/0|0|0/0/0/0|4|
|1465970|one3|Tower Defense|dev test 1 :P|3/6/15/0|25|0/0/0/0|247|
|1465971|one3|Around UNSW|dev test 1 :P|16/83/189/0|195|45/280/725/0|426|
|1465972|one3|Default|dev test 1 :P|0/0/0/0|5|2/4/9/0|39|
|1465973|one3|Queen Of Spades|dev test 1 :P|0/0/0/0|0|3/6/14/0|17|
|1465974|one3|Schooltime|dev test 1 :P|1/2/5/0|12|0/0/0/0|196|
|1465975|one3|Trophy|dev test 1 :P|0/0/0/0|0|1/2/4/0|5|
|1465976|one3|Devil|dev test 1 :P|0/0/0/0|2|73/285/653/0|365|
|1465977|one3|Trauma|dev test 1 :P|6/54/117/0|76|3/7/15/0|315|
|1465978|one3|Portals|dev test 1 :P|42/231/560/1|337|10/34/98/0|584|
|1465979|one3|Slithery Fight|dev test 1 :P|66/476/1149/0|679|2/5/15/0|930|
|1465492|one3|weakhold|WeHaveQuizzes|19/136/299/0|170|20/177/370/0|286|
|1465493|one3|Australia|WeHaveQuizzes|12/110/249/0|125|21/95/298/0|306|
|1465494|one3|Islands|WeHaveQuizzes|25/98/220/0|198|20/87/205/1|268|
|1465495|one3|Maze|WeHaveQuizzes|60/257/601/0|442|35/194/409/0|492|
|1465496|one3|Stripes|WeHaveQuizzes|0/0/0/0|1|1/4/8/0|5|
|1465497|one3|Tower Defense|WeHaveQuizzes|0/0/0/0|1|0/0/0/0|2|
|1465498|one3|Around UNSW|WeHaveQuizzes|21/109/248/0|222|36/169/422/0|461|
|1465499|one3|Default|WeHaveQuizzes|10/33/79/0|150|5/11/26/0|48|
|1465500|one3|Queen Of Spades|WeHaveQuizzes|5/12/27/0|15|1/4/9/0|13|
|1465501|one3|Schooltime|WeHaveQuizzes|32/96/226/0|204|36/108/238/0|408|
|1465502|one3|Trophy|WeHaveQuizzes|0/0/0/0|0|0/0/0/0|3|
|1465503|one3|Devil|WeHaveQuizzes|40/130/307/1|181|0/0/0/0|14|
|1465504|one3|Trauma|WeHaveQuizzes|18/84/176/0|155|21/122/263/0|309|
|1465505|one3|Portals|WeHaveQuizzes|56/512/1285/1|592|32/474/1196/1|766|
|1465506|one3|Slithery Fight|WeHaveQuizzes|60/580/1318/0|806|69/512/1234/0|926|
|1468665|one4|weakhold|dev test 1 :P|5/58/120/0|69|0/0/0/0|206|
|1468666|one4|Australia|dev test 1 :P|0/0/0/0|6|11/53/139/0|84|
|1468667|one4|Islands|dev test 1 :P|16/99/216/0|194|2/4/11/0|305|
|1468668|one4|Maze|dev test 1 :P|31/113/249/1|228|1/2/6/0|573|
|1468669|one4|Stripes|dev test 1 :P|0/0/0/0|0|0/0/0/0|6|
|1468670|one4|Tower Defense|dev test 1 :P|2/4/9/0|15|0/0/0/0|182|
|1468671|one4|Around UNSW|dev test 1 :P|22/106/235/0|201|59/345/1051/0|517|
|1468672|one4|Default|dev test 1 :P|0/0/0/0|3|0/0/0/0|47|
|1468673|one4|Queen Of Spades|dev test 1 :P|13/49/118/0|60|4/10/25/0|17|
|1468674|one4|Schooltime|dev test 1 :P|1/2/5/0|14|0/0/0/0|170|
|1468675|one4|Trophy|dev test 1 :P|0/0/0/0|0|0/0/0/0|5|
|1468676|one4|Devil|dev test 1 :P|1/2/4/0|6|36/148/327/0|199|
|1468677|one4|Trauma|dev test 1 :P|5/55/113/0|109|2/5/13/0|342|
|1468678|one4|Portals|dev test 1 :P|65/473/1205/1|578|7/25/65/0|576|
|1468679|one4|Slithery Fight|dev test 1 :P|58/559/1308/0|726|0/0/0/0|1055|
|1470217|one4|weakhold|WeHaveQuizzes|8/94/200/0|110|33/248/516/1|383|
|1470218|one4|Australia|WeHaveQuizzes|18/66/150/0|141|17/107/253/0|340|
|1470219|one4|Islands|WeHaveQuizzes|19/104/228/0|173|27/116/270/0|359|
|1470220|one4|Maze|WeHaveQuizzes|45/181/401/0|303|38/264/562/0|612|
|1470221|one4|Stripes|WeHaveQuizzes|4/13/27/1|13|9/77/168/0|92|
|1470222|one4|Tower Defense|WeHaveQuizzes|0/0/0/0|3|14/37/87/0|217|
|1470223|one4|Around UNSW|WeHaveQuizzes|20/104/241/0|210|37/176/442/0|415|
|1470224|one4|Default|WeHaveQuizzes|14/37/91/0|127|5/13/30/0|39|
|1470225|one4|Queen Of Spades|WeHaveQuizzes|8/36/81/0|41|3/9/23/0|27|
|1470226|one4|Schooltime|WeHaveQuizzes|65/237/549/0|339|50/150/382/0|497|
|1470227|one4|Trophy|WeHaveQuizzes|3/7/18/0|12|0/0/0/0|0|
|1470228|one4|Devil|WeHaveQuizzes|0/0/0/0|2|2/4/9/0|23|
|1470229|one4|Trauma|WeHaveQuizzes|5/27/55/0|67|28/119/251/0|312|
|1470230|one4|Portals|WeHaveQuizzes|50/518/1332/1|581|33/454/1145/1|715|
|1470231|one4|Slithery Fight|WeHaveQuizzes|65/276/662/1|441|90/608/1457/0|1154|
|1472752|one5|weakhold|Cache me outside|20/136/288/1|201|4/18/42/0|35|
|1472753|one5|Australia|Cache me outside|12/45/101/0|106|54/301/960/1|446|
|1472754|one5|Islands|Cache me outside|29/136/309/1|269|52/291/709/1|421|
|1472755|one5|Maze|Cache me outside|52/193/435/1|382|101/456/1035/0|552|
|1472756|one5|Stripes|Cache me outside|8/63/134/1|75|12/90/194/1|120|
|1472757|one5|Tower Defense|Cache me outside|0/0/0/0|3|66/192/455/1|254|
|1472758|one5|Around UNSW|Cache me outside|11/56/128/0|150|124/661/1727/1|805|
|1472759|one5|Default|Cache me outside|1/2/4/0|44|6/12/30/0|45|
|1472760|one5|Queen Of Spades|Cache me outside|11/50/120/0|79|5/20/44/1|33|
|1472761|one5|Schooltime|Cache me outside|24/59/158/0|191|120/442/1143/0|598|
|1472762|one5|Trophy|Cache me outside|0/0/0/0|0|5/22/55/0|40|
|1472763|one5|Devil|Cache me outside|0/0/0/0|0|37/121/273/0|165|
|1472764|one5|Trauma|Cache me outside|2/23/47/0|70|75/358/794/0|475|
|1472765|one5|Portals|Cache me outside|42/475/1250/1|579|84/487/1209/1|538|
|1472766|one5|Slithery Fight|Cache me outside|55/473/1074/0|585|166/1034/2653/1|1196|
|1471456|one5|weakhold|dev test 1 :P|7/103/222/0|132|0/0/0/0|189|
|1471457|one5|Australia|dev test 1 :P|0/0/0/0|0|8/44/131/0|67|
|1471458|one5|Islands|dev test 1 :P|27/106/240/0|183|2/4/9/0|259|
|1471459|one5|Maze|dev test 1 :P|45/208/483/1|415|0/0/0/0|483|
|1471460|one5|Stripes|dev test 1 :P|0/0/0/0|7|0/0/0/0|17|
|1471461|one5|Tower Defense|dev test 1 :P|0/0/0/0|2|0/0/0/0|7|
|1471462|one5|Around UNSW|dev test 1 :P|23/113/251/0|234|59/351/912/0|505|
|1471463|one5|Default|dev test 1 :P|0/0/0/0|18|0/0/0/0|149|
|1471464|one5|Queen Of Spades|dev test 1 :P|6/20/47/0|25|4/12/29/0|38|
|1471465|one5|Schooltime|dev test 1 :P|101/325/785/0|522|0/0/0/0|272|
|1471466|one5|Trophy|dev test 1 :P|0/0/0/0|0|0/0/0/0|0|
|1471467|one5|Devil|dev test 1 :P|0/0/0/0|4|17/65/146/0|95|
|1471468|one5|Trauma|dev test 1 :P|3/16/32/0|28|0/0/0/0|281|
|1471469|one5|Portals|dev test 1 :P|54/461/1179/1|533|8/26/66/0|585|
|1471470|one5|Slithery Fight|dev test 1 :P|64/632/1505/0|841|2/5/18/0|918|
|1472003|one5|weakhold|WeHaveQuizzes|5/81/170/0|96|28/235/494/0|383|
|1472004|one5|Australia|WeHaveQuizzes|24/144/328/0|248|9/37/84/0|170|
|1472005|one5|Islands|WeHaveQuizzes|21/95/219/0|176|26/102/247/0|303|
|1472006|one5|Maze|WeHaveQuizzes|46/180/406/0|335|35/223/482/0|505|
|1472007|one5|Stripes|WeHaveQuizzes|0/0/0/0|0|6/26/57/0|28|
|1472008|one5|Tower Defense|WeHaveQuizzes|0/0/0/0|5|24/68/145/0|241|
|1472009|one5|Around UNSW|WeHaveQuizzes|24/104/256/0|236|46/232/562/0|488|
|1472010|one5|Default|WeHaveQuizzes|4/10/26/0|20|2/4/8/0|38|
|1472011|one5|Queen Of Spades|WeHaveQuizzes|12/52/129/0|71|0/0/0/0|1|
|1472012|one5|Schooltime|WeHaveQuizzes|0/0/0/0|7|23/61/181/0|233|
|1472013|one5|Trophy|WeHaveQuizzes|1/3/7/0|7|0/0/0/0|1|
|1472014|one5|Devil|WeHaveQuizzes|17/50/116/0|84|0/0/0/0|3|
|1472015|one5|Trauma|WeHaveQuizzes|15/68/146/0|115|30/133/278/0|340|
|1472016|one5|Portals|WeHaveQuizzes|54/481/1216/1|574|32/475/1205/0|762|
|1472017|one5|Slithery Fight|WeHaveQuizzes|51/356/751/0|512|91/535/1358/0|1040|
|1461163|one1|Devil|Cache me outside|4/12/28/0|29|65/298/667/1|361|
|1461164|one1|Default|Cache me outside|12/33/99/0|101|2/6/15/0|18|
|1461165|one1|Slithery Fight|Cache me outside|50/401/883/0|637|163/956/2426/1|1090|
|1461166|one1|Queen Of Spades|Cache me outside|6/15/37/0|23|8/24/58/0|33|
|1461167|one1|Australia|Cache me outside|9/71/163/0|117|63/277/943/0|412|
|1462081|one1|weakhold|Knight Capital|40/185/407/1|251|9/197/434/0|205|
|1462082|one1|Trauma|Knight Capital|4/36/76/0|73|50/206/471/0|314|
|1462083|one1|Default|Knight Capital|14/33/73/0|124|4/12/26/0|27|
|1462084|one1|Queen Of Spades|Knight Capital|1/2/4/0|6|3/10/27/0|16|
|1462085|one1|Prisoners Dilemma|Knight Capital|2/7/15/1|8|3/18/36/0|19|
|1466570|one3|Islands|WeHaveQuizzes|8/19/43/0|93|45/161/444/1|365|
|1466571|one3|Default|WeHaveQuizzes|8/20/53/0|91|6/16/41/0|61|
|1466572|one3|Trauma|WeHaveQuizzes|11/62/133/0|91|31/145/311/0|376|
|1466573|one3|Prisoners Dilemma|WeHaveQuizzes|2/5/10/0|7|0/0/0/0|2|
|1466574|one3|Queen Of Spades|WeHaveQuizzes|1/5/13/0|13|3/11/28/0|27|
|1467174|one3|Portals|中国必须人能飞😡|49/499/1271/1|576|61/288/674/0|404|
|1467175|one3|Stripes|中国必须人能飞😡|6/37/77/1|45|13/67/146/1|86|
|1467176|one3|Slithery Fight|中国必须人能飞😡|56/466/1080/0|592|96/565/1283/0|707|
|1467177|one3|Autarky|中国必须人能飞😡|7/68/141/0|84|2/21/42/0|24|
|1467178|one3|Prisoners Dilemma|中国必须人能飞😡|4/13/27/1|14|1/2/4/0|4|
|1467565|one3|Maze|tozoman|55/214/520/0|460|31/91/205/0|152|
|1468124|one3|Slithery Fight|Codehammer 40K|54/405/1023/0|496|136/518/1588/0|750|
|1468125|one3|Tower Defense|Codehammer 40K|3/8/17/0|29|0/0/0/0|4|
|1468126|one3|Stripes|Codehammer 40K|0/0/0/0|1|4/24/49/0|31|
|1468127|one3|weakhold|Codehammer 40K|38/185/402/0|247|15/144/299/0|157|
|1468128|one3|Islands|Codehammer 40K|44/181/449/0|309|14/61/159/0|170|
|1470539|one4|Slithery Fight|Poisoned Pigeon in the Park|77/486/1150/0|688|93/861/2062/0|985|
|1470540|one4|Australia|Poisoned Pigeon in the Park|24/255/569/0|304|17/51/144/0|130|
|1470541|one4|Default|Poisoned Pigeon in the Park|7/15/35/0|36|0/0/0/0|1|
|1470542|one4|Islands|Poisoned Pigeon in the Park|23/72/168/0|138|46/295/624/0|436|
|1470543|one4|Stripes|Poisoned Pigeon in the Park|2/10/21/1|14|2/6/12/0|10|
|1471964|one5|Devil|Jingling Munmin|17/45/108/1|73|0/0/0/0|3|
|1471965|one5|Maze|Jingling Munmin|32/134/311/0|260|36/138/293/0|380|
|1471966|one5|Stripes|Jingling Munmin|3/15/31/0|18|8/30/66/0|49|
|1471967|one5|Default|Jingling Munmin|0/0/0/0|11|5/10/25/0|148|
|1471968|one5|Schooltime|Jingling Munmin|16/45/119/0|160|0/0/0/0|16|
|1473235|one5|Portals|tozoman|45/488/1267/1|568|41/171/678/1|274|
|1473236|one5|Autarky|tozoman|16/124/258/0|145|3/6/14/0|14|
|1473237|one5|Islands|tozoman|29/111/304/0|306|22/92/219/0|149|
|1473238|one5|Devil|tozoman|11/27/66/0|42|1/2/6/0|11|
|1473239|one5|Stripes|tozoman|6/49/102/0|53|26/85/206/0|115|
