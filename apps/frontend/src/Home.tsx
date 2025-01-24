import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div>
      <h1>ホーム画面</h1>
      <Button variant="contained" onClick={() => navigate("/setup")}>
        会議の初期設定画面
      </Button>
      <Button variant="contained" onClick={() => navigate("/join")}>
        会議参加画面
      </Button>
    </div>
  );
};

export default Home;
