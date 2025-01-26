import { useNavigate } from "react-router-dom";
import { Button, Container, Typography, Box, TextField } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useState } from "react";

const Home = () => {
  const navigate = useNavigate();
  const [meetingCode, setMeetingCode] = useState("");

  return (
    <Container
      maxWidth="md"
      sx={{
        backgroundColor: "rgba(255, 255, 255, 0.8)",
        borderRadius: "12px",
        padding: "50px",
        boxShadow: 5,
        textAlign: "center",
        mt: 6,
        backdropFilter: "blur(10px)",
        backgroundImage: "url('/path/to/background.jpg')",
        backgroundSize: "cover",
      }}
    >
      <Typography
        variant="h3"
        gutterBottom
        sx={{ fontWeight: "bold", mt: 3, color: "#333" }}
      >
        AI Agentがあなたをサポート
      </Typography>
      <Typography variant="body1" gutterBottom sx={{ mt: 2, color: "#555" }}>
        AI Agentがビデオ会議をよりスムーズにサポートします。
        <br />
        AIの力で、会議の効率を最大限に引き出しましょう。
      </Typography>
      <Box mt={4}>
        <Button
          variant="contained"
          color="primary"
          fullWidth
          onClick={() => navigate("/setup")}
          sx={{
            mb: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "12px 24px",
            fontSize: "18px",
            transition: "background-color 0.3s",
            "&:hover": {
              backgroundColor: "#0056b3",
            },
          }}
        >
          <ArrowForwardIcon sx={{ mr: 1 }} />
          会議の初期設定画面
        </Button>
      </Box>
      <Box mt={4}>
        <TextField
          fullWidth
          placeholder="コードを入力"
          variant="outlined"
          sx={{ mb: 2, backgroundColor: "white", borderRadius: "4px" }}
          onChange={(e) => setMeetingCode(e.target.value)}
        />
        <Button
          variant="contained"
          color="secondary"
          fullWidth
          onClick={() => navigate(`/meeting/${meetingCode}`)}
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "12px 24px",
            fontSize: "18px",
            transition: "background-color 0.3s",
            "&:hover": {
              backgroundColor: "#c51162",
            },
          }}
        >
          今すぐ会議に参加する
        </Button>
      </Box>
    </Container>
  );
};

export default Home;
