import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>会議管理システムだよ</h1>
      <button onClick={() => navigate("/setup")}>会議を設定する</button>
      <button onClick={() => navigate("/auth")}>会議に参加する</button>
    </div>
  );
};

export default Home;
