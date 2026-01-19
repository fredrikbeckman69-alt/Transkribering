# Svensk Transkrebering - Webapp

En webbaserad applikation för att transkribera svenskt tal till text med hjälp av AI (KBLab Whisper).

## Funktioner

*   **Ingen installation krävs:** Körs direkt i webbläsaren.
*   **AI-driven:** Använder KBLab:s kraftfulla Whisper-modell för svenska.
*   **Filuppladdning:** Dra och släpp ljudfiler direkt i fönstret.
*   **Kräver API Token:** Du måste ha en Hugging Face API-token (gratis) konfigurerad eftersom modellen kräver autentisering.
*   **Modern Design:** Premium dark-mode gränssnitt.

## Hur man använder appen

1.  Gå till mappen `Svensk transkribering`.
2.  **Konfigurera Token:** Se till att miljövariabeln `HF_TOKEN` är satt, eller redigera `start_app.bat` (avancerat).
3.  **Kör filen `start_app.bat`** (dubbelklicka).
    *   Detta startar en lokal webbserver.
4.  Webbläsaren öppnas automatiskt.
5.  **Ladda upp fil:** Klicka på rutan eller dra in en ljudfil (.mp3, .wav, etc.).
6.  **Transkribera:** Klicka på knappen.

## Teknisk Info

Lösningen är byggd med "Vanilla" JavaScript, HTML och CSS för att vara så lättviktig och portabel som möjligt. Den ansluter direkt till Hugging Face Inference API.

*   `index.html`: Struktur
*   `style.css`: Design
*   `app.js`: Logik och API-anrop
