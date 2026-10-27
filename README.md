# Savdo Daftari

Do'kon hisob-kitobi: savdo, mijozlar qarzi, kassa, rasxod, ombor, prixod, hisobot va foyda. Guruhlar bo'yicha alohida kassa (Weslamic, iQIBLA, Joynamoz, Mayda tasbehlar).

Sayt: GitHub Pages orqali ochiladi. Ma'lumotlar Firebase Firestore'da saqlanadi, shuning uchun barcha xodimlar bitta bazani ko'radi.

## Sozlash

1. [Firebase Console](https://console.firebase.google.com) da yangi loyiha oching (bepul Spark tarifi yetarli).
2. **Build → Firestore Database → Create database** (test mode).
3. **Project settings → Your apps → Web app (</>)** qo'shing va chiqqan `firebaseConfig` qiymatlarini `firebase-config.js` ga nusxalang.
4. Saytni oching, birinchi kirishda rahbar login/parol yaratiladi.

## Fayllar

- `index.html` — butun dastur (bir fayl)
- `firebase-config.js` — Firebase ulanish sozlamalari
