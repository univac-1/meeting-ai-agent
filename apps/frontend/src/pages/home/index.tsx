import { version } from "../../../package.json"
import { useNavigate } from "react-router-dom"

import styles from "./index.module.scss"
import logoSrc from "@/assets/logo.jpg"

const HomePage = () => {
  const nav = useNavigate()

  const onClickSchedule = () => {
    nav("/meeting/schedule")
  }

  const onClickJoin = () => {
    nav("/join")
  }

  return (
    <div className={styles.homePage}>
      <section className={styles.content}>
        <div className={styles.title}>
          <div className={styles.logo}>
            <img src={logoSrc} alt="" />
          </div>
          {/* <div className={styles.text}>Meeting With AI Agent</div> */}
        </div>
        <div className={styles.btn} onClick={onClickSchedule}>
          Schedule Meeting
        </div>
        <div className={styles.btn} onClick={onClickJoin}>
          Join Meeting
        </div>
      </section>
    </div>
  )
}

export default HomePage
