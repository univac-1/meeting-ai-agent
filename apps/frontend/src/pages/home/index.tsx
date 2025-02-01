import { useTranslation } from "react-i18next"
import { version } from "../../../package.json"
import { useNavigate } from "react-router-dom"

import styles from "./index.module.scss"
import logoSrc from "@/assets/login_logo.png"

const HomePage = () => {
  const nav = useNavigate()
  const { t, i18n } = useTranslation()

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
          <div className={styles.text}>{t("home.title")}</div>
        </div>
        <div className={styles.btn} onClick={onClickSchedule}>
          {t("home.schedule")}
        </div>
        <div className={styles.btn} onClick={onClickJoin}>
          {t("home.join")}
        </div>
        <div className={styles.version}>Version {version}</div>
      </section>
    </div>
  )
}

export default HomePage
