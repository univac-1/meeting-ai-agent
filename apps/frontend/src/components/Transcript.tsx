import React, { useEffect, useState, useRef } from "react";
import { Box, Typography } from "@mui/material";
import { db } from "../firebase";
import { collection, onSnapshot, orderBy, query } from "firebase/firestore";

interface Transcript {
  speaker: string;
  message: string;
  speak_at: string;
}

const Transcript: React.FC<{ meetingId: string }> = ({ meetingId }) => {
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const transcriptEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const commentsRef = collection(db, "meetings", meetingId, "comments");
    const q = query(commentsRef, orderBy("speak_at"));

    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const messageHistory: Transcript[] = [];
      querySnapshot.forEach((doc) => {
        messageHistory.push(doc.data() as Transcript);
      });
      setTranscripts(messageHistory);
      console.log('Updated Firestore transcripts:', messageHistory);
    });

    // クリーンアップ関数でリスナーを解除
    return () => unsubscribe();
  }, [meetingId]);

  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [transcripts]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString("ja-JP", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <Box
      sx={{
        width: 300,
        height: "100vh",
        overflowY: "auto",
        position: "fixed",
        right: 0,
        top: 0,
        bgcolor: "background.default",
        boxShadow: 3,
        p: 2,
      }}
    >
      <Typography variant="h6" gutterBottom>
        トランスクリプト
      </Typography>
      {transcripts.map((transcript, index) => (
        <Box key={index} mb={2}>
          <Typography variant="body2" color="black">
            {formatTimestamp(transcript.speak_at)} - {transcript.speaker}
          </Typography>
          <Typography variant="body1" color="black">
            {transcript.message}
          </Typography>
        </Box>
      ))}
      <div ref={transcriptEndRef} />
    </Box>
  );
};

export default Transcript;
