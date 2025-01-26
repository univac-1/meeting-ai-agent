import "core-js/stable";
import "regenerator-runtime/runtime";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import {
  LocalUser,
  RemoteUser,
  useIsConnected,
  useJoin,
  useLocalMicrophoneTrack,
  useLocalCameraTrack,
  usePublish,
  useRemoteUsers,
} from "agora-rtc-react";
import {
  Button,
  TextField,
  Box,
  Stack,
  IconButton,
  Typography,
} from "@mui/material";
import {
  Mic,
  MicOff,
  Videocam,
  VideocamOff,
  Call,
  CallEnd,
  ArrowForward,
} from "@mui/icons-material";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import axios from "axios";
import "./index.css";
import { CLOUD_RUN_ENDPOINT } from "./config";
import Transcript from "./components/Transcript";

const APP_ID = "dfd31dd0fc764a25b5bba0bbac2d5ef6";

export const MeetingApp = () => {
  const [calling, setCalling] = useState(false);
  const isConnected = useIsConnected();
  const [channel, setChannel] = useState("");
  const [uid, setUid] = useState("");
  const { meetingId } = useParams<{ meetingId: string }>();
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [showTranscript, setShowTranscript] = useState(false);

  useEffect(() => {
    const getVoices = () => {
      setVoices(window.speechSynthesis.getVoices());
    };
    getVoices();
    window.speechSynthesis.onvoiceschanged = getVoices;
  }, []);

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voices.find((voice) => voice.lang === "ja-JP") || null;
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    if (meetingId) {
      setChannel(meetingId);
    }
  }, [meetingId]);

  useJoin({ appid: APP_ID, channel, uid: uid, token: null }, calling);

  const [micOn, setMic] = useState(true);
  const [cameraOn, setCamera] = useState(true);
  const { localMicrophoneTrack } = useLocalMicrophoneTrack(micOn);
  const { localCameraTrack } = useLocalCameraTrack(cameraOn);
  usePublish([localMicrophoneTrack, localCameraTrack]);

  const remoteUsers = useRemoteUsers();

  const { transcript, listening, browserSupportsSpeechRecognition } =
    useSpeechRecognition();

  useEffect(() => {
    if (isConnected) {
      if (micOn) {
        if (!listening) {
          SpeechRecognition.startListening();
        }
      } else {
        if (listening) {
          SpeechRecognition.stopListening();
        }
      }
    } else {
      if (listening) {
        SpeechRecognition.stopListening();
      }
    }
  }, [listening, browserSupportsSpeechRecognition, micOn, isConnected]);

  // 会議参加後、マイクオンで発言するたびに、発言内容をAPIに送信する
  useEffect(() => {
    if (isConnected && !listening && micOn && transcript) {
      console.log(transcript);
      console.log("==== 区切り ====");
      axios
        .post(
          `${CLOUD_RUN_ENDPOINT}/message`,
          {
            meeting_id: channel,
            speaker: uid,
            message: transcript,
          },
          {
            headers: {
              "Content-type": "application/json; charset=UTF-8",
            },
          }
        )
        .then((response) => console.log(response.data))
        .catch((error) => console.error("Error:", error));
    }
  }, [listening, micOn, isConnected]);

  // AI Agentボタンクリック時の処理
  const handleAIAgentClick = () => {
    console.log("AI AGENT button clicked");
    axios
      .get(`${CLOUD_RUN_ENDPOINT}/meeting/${channel}/agent-feedback`)
      .then((response) => console.log(response.data))
      .catch((error) => console.error("Error:", error));
    // 音声合成する場合
    speak("AI Agentを呼び出します");
  };

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser doesn't support speech recognition.</span>;
  }

  return (
    <>
      <div className="room">
        {isConnected ? (
          <div className="user-list">
            <div className="user">
              <LocalUser
                audioTrack={localMicrophoneTrack}
                cameraOn={cameraOn}
                micOn={micOn}
                videoTrack={localCameraTrack}
                cover="https://www.agora.io/en/wp-content/uploads/2022/10/3d-spatial-audio-icon.svg"
              >
                <samp className="user-name">{uid} (You)</samp>
              </LocalUser>
            </div>
            {remoteUsers.map((user) => (
              <div className="user" key={user.uid}>
                <RemoteUser
                  cover="https://www.agora.io/en/wp-content/uploads/2022/10/3d-spatial-audio-icon.svg"
                  user={user}
                >
                  <samp className="user-name">{user.uid}</samp>
                </RemoteUser>
              </div>
            ))}
          </div>
        ) : (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: 2,
              width: 400,
              p: 3,
              bgcolor: "background.paper",
              borderRadius: 2,
              boxShadow: 3,
            }}
          >
            <Typography variant="h5" component="h2" gutterBottom color="black">
              Join Video Call
            </Typography>
            <TextField
              label="Channel Name"
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              fullWidth
              variant="outlined"
              size="small"
            />
            <TextField
              label="User Name"
              value={uid}
              onChange={(e) => {
                const newValue = e.target.value.replace(/[^a-zA-Z0-9]/g, "");
                setUid(newValue);
              }}
              fullWidth
              variant="outlined"
              size="small"
            />
            <Button
              variant="contained"
              endIcon={<ArrowForward />}
              onClick={() => setCalling(true)}
              disabled={!APP_ID || !channel || !uid}
              fullWidth
              sx={{ mt: 2 }}
            >
              Join Channel
            </Button>
          </Box>
        )}
      </div>
      {isConnected && (
        <Stack
          direction="row"
          spacing={2}
          sx={{
            position: "fixed",
            bottom: 32,
            left: "50%",
            transform: "translateX(-50%)",
            p: 2,
            bgcolor: "background.paper",
            borderRadius: 4,
            boxShadow: 3,
          }}
        >
          <IconButton
            color={micOn ? "primary" : "default"}
            onClick={() => setMic((a) => !a)}
          >
            {micOn ? <Mic /> : <MicOff />}
          </IconButton>
          <IconButton
            color={cameraOn ? "primary" : "default"}
            onClick={() => setCamera((a) => !a)}
          >
            {cameraOn ? <Videocam /> : <VideocamOff />}
          </IconButton>
          <Button
            variant="contained"
            color={calling ? "error" : "primary"}
            onClick={() => setCalling((a) => !a)}
            startIcon={calling ? <CallEnd /> : <Call />}
            sx={{ px: 4 }}
          >
            {calling ? "End Call" : "Start Call"}
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={handleAIAgentClick}
            sx={{ px: 4 }}
          >
            AI AGENT
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => setShowTranscript((prev) => !prev)}
            sx={{ px: 4 }}
          >
            {showTranscript ? "Hide Transcript" : "Show Transcript"}
          </Button>
        </Stack>
      )}
      {isConnected && showTranscript && <Transcript meetingId={channel} />}
    </>
  );
};

export default MeetingApp;
