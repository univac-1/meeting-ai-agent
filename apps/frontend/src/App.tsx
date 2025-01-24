import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home";
import MeetingSetup from "./MeetingSetup";
import MeetingURLConfirmation from "./MeetingURLConfirmation";
import MeetingApp from "./MeetingApp";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/setup" element={<MeetingSetup />} />
        <Route path="/confirmation" element={<MeetingURLConfirmation />} />
        <Route path="/meeting" element={<MeetingApp />} />
      </Routes>
    </Router>
  );
};

export default App;
