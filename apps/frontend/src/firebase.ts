import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
    apiKey: "AIzaSyACYfH9xsYTUQG9KVdcXwsq0AEtUan2UnQ",
    authDomain: "ai-agent-hackthon-with-goole.firebaseapp.com",
    projectId: "ai-agent-hackthon-with-goole",
    storageBucket: "ai-agent-hackthon-with-goole.firebasestorage.app",
    messagingSenderId: "132459894103",
    appId: "1:132459894103:web:00d8dadaf8b1212e65da12"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app, 'ai-agent-cfs');

export { db };
