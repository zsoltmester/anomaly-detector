# Forrás

https://www.dropbox.com/preview/documents/ELTE/szakdolgozat-informaciok.pdf?role=personal
https://www.dropbox.com/preview/documents/ELTE/Szakdolgozat%20%C3%A9rt%C3%A9kel%C3%A9s.pdf?role=personal
https://mail.google.com/mail/u/0/#label/ELTE/15fe91786be6ba96

# Tartalomi követelmény

- Bevezetés
- Felhasználói dokumentáció
- Fejlesztői dokumentáció

## Bevezetés

A Bevezetés a témaválasztás indoklását és a megoldandó feladat rövid, közérthető leírását tartalmazza.

## Felhasználói dokumentáció

A felhasználói dokumentáció tartalmazza
- a megoldott probléma rövid megfogalmazását,
- a felhasznált módszerek rövid leírását,
- a program használatához szükséges összes információt.

A bírálatból:
- A feladatrövid ismertetése (mire való a szoftver)
- Célközönség (kik, mikor, mire használhatják a programot)
- A rendszer használatához szükséges minimális, illetve optimális HW/SW környezet
- Első üzembehelyezés leírása -ha van ilyen-, a program indítása(kivéve, ha nem egy önálló alkalmazásról, hanem egy meglévő rendszer új komponenséről van szó). Itt ellenőrizzük, hogy a telepítési útmutató megfelel-e a valóságos telepítési folyamatnak.
- Általános felhasználói tájékoztató (például a szokásostól eltérő képernyő-, billentyű-, illetve egérkezelés leírása, teendők hibaüzenetek esetén stb.).
- A rendszer funkcióinak ismertetése. A feladat jellegéből fakadóan célszerű lehet ezt folyamatszerűen, képernyőképekkel alátámasztva bemutatni. A funkciókat ajánlatos a felhasználói szintek szerint csoportosítani. Itt vegyük figyelembe, hogy a leírás a fejlesztői dokumentációban meghatározott részfeladathoz illeszkedik-e, az ott meghatározott funkciókat/használati eseteket írja-e le?
- A rendszer futás közbeni üzenetei (hibaüzenetek, figyelmeztető üzenetek, felszólító üzenetek stb.) és azok magyarázata - az esetleges üzemeltetési teendőkkel együtt. Itt vegyük figyelembe, hogy tartalmaz-e biztonsági, illetve hibaelhárítási előírásokat?
- Egyéb, a szoftver használatához szükséges információk.

## Fejlesztői dokumentáció

A fejlesztői dokumentáció tartalmazza
- a probléma részletes specifikációját,
- a felhasznált módszerek részletes leírását, a használt fogalmak definícióját,
- a program logikai és fizikai szerkezetének leírását (adatszerkezetek, adatbázisok, modulfelbontás),
- a tesztelési tervet és a tesztelés eredményeit.

### Megoldási terv

Ez a fejlesztői leírás része, a rendszerterv, amelyből az alkalmazás célja, felépítése és működése megérthető, ez alapján az alkalmazás forráskódja lényegében elkészíthető.

Tartalmazza a következő elemeket:
- Rendszer architektúrájának leírását (alrendszerek, rétegek bemutatása, az alkalmazott szabványok, technológiák, fejlesztő módszerek megadása, felhasznált eszközök és kész komponensek definiálása). Az értékelésnél vegyük figyelembe, hogy mennyire válnak szét az alkalmazás rétegei (például felhasználói felület, logika, adatforrás)?
- Az adatbázis -feltéve, hogy van- leírását. Érdemes egy áttekintő diagammal szemléltetni a táblákat és a köztük levő kapcsolatokat, majd külön táblázatokban megadni az egyes táblák mezőszerkezeti leírását, az esetleges tárolt eljárások, függvények, triggerek, stb leírását.
- Modul és/vagy osztályszerkezet (fontosabb modulok és/vagy osztályok és azok metódusai, továbbá ezek kapcsolatának) leírását. Az egyes csomagok fő eljárásait illetve a fontos osztályok fő metódusait bemenő-, kimenőadat, tevékenység hármassal jellemezni kell.
- A felhasználói felület -feltéve, hogy van- tervét (a képernyő- és listaterveket, valamint a menütervet). Legyen egy áttekintő ábra, amely mutatja a képernyők (ablakok, weblapok) közti navigálási lehetőségeket, irányokat. Ki kell emelni a fontosabb felhasználói eseménykezeléseket.

### Megvalósítás

A fejlesztői leírásnak a megvalósításról szóló része bemutatja, hogy milyen döntéseket kellett hozni a terv megvalósítása során (adatábrázolás, felhasznált komponensek, kódban alkalmazott nyelvi elemek, stb). A dokumentáció ne tartalmazza a forrásprogramot (legfeljebb csak fontosnak ítélt részleteit), elég azt a mellékelt adathordozón elhelyezni. A megvalósítás a fentieken kívül tartalmazza a komponens tervet (az alkalmazás fizikai komponenseinek kapcsolatrendszerét) és azok telepítésének módját.

Az értékelésnél vegyük figyelembe:
- A forráskód tartalma, szerkezete megfelel-e a tervnek?
- Mennyire ismeri a hallgató az adott fejlesztő eszközt (pl. korszerű, hatékony nyelvi elemek vannak-e túlsúlyban, vagy ehelyett bonyolult, nehézkes, körülményes és leginkább terjengős forráskódot eredményező nyelvi elemek jellemzik a kódot)? Indokoltak-e a választott nyelvi elemek használata?
- Milyen a forráskód külalakja, mennyire áttekinthető (strukturáltság, bekezdések, tagolások, kommentezés stb.)?
- Mennyire módosítható a kód. Alkalmazza-e a hallgató a kód-újrafelhasználás nyelvi eszközeit (függvények, származtatás, generikus elemek)?
- Törekszik-e a hatékony adatábrázolásra?
- Mennyire öndokumentáló a kód, vagyis a választott azonosítók (pl. változónevek) mennyire beszédesek, konvencionálisak, a megjegyzések mennyire segítik a kódértést?
- Tartalmazza a szükséges ellenőrzési, hibakezelési funkciókat, általában megoldott-e a kivételkezelés?
- Mennyire gazdálkodik jól az emberi és gépi erőforrásokkal, így például a felhasználó idejével és türelmével, a lemezkapacitással és a memóriakapacitással?

### Tesztelés

Ez is a fejlesztői leírás része, amelynek a tesztelési szempontokat kell bemutatnia, és a tesztelés során szerzett tapasztalatokat összegeznie valamint a szoftver skálázhatóságáról készített elemzést kell tartalmaznia.

Az értékelésnél vegyük figyelembe, hogy a dokumentáció:
- Tartalmaz-e tesztelési terveket, teszteseteket (Ezeket csoportosíthatja rendszerteszt és modultesztek szerint illetve fekete és fehérdoboz megközelítéssel)?
- Beszámol-e olyan tanulságokról, amelyek alapján meg kellett változtatni a korábbi implementációs döntéseket, esetleg a terv egyes elemeit (az ilyen tapasztalatok nem rontják a dolgozat értékét)?
- Tartalmazza-e nagy adattömeg melletti futtatások értékelését?
- Elemzi-e a program által adott eredmény helyességét (különösen olyan optimalizációs feladatok esetén, ahol több helyes megoldást valamilyen célfüggvénnyel lehet rangsorolni)?
- Elemzi-e a program futásának hatékonyságát?

# Formai követelmények

- A szakdolgozatot nyomtatva, bekötve kell benyújtani.
- A szakdolgozat első oldalának fejlécében szerepeljen az ELTE emblémája, az egyetem, a kar és a témavezető tanszékének neve. Az oldaltörzsében fel kell tüntetni a szakdolgozat címét, szerzőjének nevét, szakját, a témavezető nevét,a külső konzulens nevét,a beadás helyét és a védés évét.
- A dolgozat 2. oldala a hivatalos Szakdolgozat-téma bejelentő.
- A szakdolgozatnak tartalmaznia kell a II. pontban kötelezően előírt három fejezetet (Bevezető, Felhasználói dokumentáció, Fejlesztői dokumentáció).
- A dolgozatot el kell látni tartalomjegyzékkel - és ha ezt a téma szükségessé teszi-irodalomjegyzékkel is.
- Amennyiben a hallgató munkájához másoktól származó eredményeket is felhasznál, akkor ezek forrását meg kell neveznie.

A szakdolgozatra vonatkozó formai követelmények további részletezését az 1. számú melléklet tartalmazza.
- 1. Melléklet: https://www.dropbox.com/preview/documents/ELTE/szakdolgozat-informaciok.pdf?role=personal

# Bírálat

https://www.dropbox.com/preview/documents/ELTE/Szakdolgozat%20%C3%A9rt%C3%A9kel%C3%A9s.pdf?role=personal

# Beadás

Határidő: december 15.

A program forrásnyelvi szövegét elektronikus formában mellékelni kell(az adathordozót a kemény borító hátlapjának belső oldalára ragasztott papírtokba helyezve).

1 példány bekötve, program DVD-n és 1 DVD a Kari Könyvtár részére.

A szakdolgozat/diplomamunka leadásakor kérjük Önöktől:
- 1 példány bekötött dolgozatot, mellékelve a program
- eredetiség nyilatkozatot,
- elhelyezési megállapodást ELTE Digitális Intézményi Tudástár (EDIT)
- EDIT Hallgatói dolgozat űrlapot
- DVD-t - a nyomtatott dolgozattal azonos tartalmú, PDF/A formátumú dolgozat, plusz program, a DVD-n/külső borítóján legyenek szívesek feltüntetni nevüket, Neptun azonosítójukat és az évszámot.

A szükséges nyomtatványokat a Hivatal honlapján elérhetik: https://www.inf.elte.hu/content/adatlapok-formanyomtatvanyok.t.1052?m=129
