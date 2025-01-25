import { useNavigate } from "react-router-dom";
import { Button, Container, Typography, Box } from "@mui/material";

const Home = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box textAlign="center" mt={5}>
        <Typography variant="h4" gutterBottom>
          ホーム画面
        </Typography>
        <Box mt={2}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={() => navigate("/setup")}
            sx={{ mb: 2 }}
          >
            会議の初期設定画面
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Home;
