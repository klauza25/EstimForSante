   /** @type {import('tailwindcss').Config} */
   module.exports = {
     content: [
       "./*.html",        // Inclut tous les fichiers HTML dans le répertoire racine
       "./**/*.html",     // Inclut tous les fichiers HTML dans les sous-dossiers
     ],
     theme: {
       extend: {},
     },
     plugins: [],
   }