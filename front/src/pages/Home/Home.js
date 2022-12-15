import React from 'react'
import { Link } from 'react-router-dom'

import './Home.css'

export default function Home() {

    return (
        <div className='home-container'>
            <h1 className="description">AI Fitness Coach</h1>
            <div className="home-left">
            </div>
            <div className-="home-right">
                <div className="intro">
                    <h3>Introduction</h3>
                    <h5>1. 请确保你已经授予了摄像头的权限</h5>
                    <h5>2. 确认当时没有任何其他应用程序访问相机，如果有，请关闭该应用程序</h5>
                    <h5>3. 在下拉菜单中选择想要学习的动作</h5>
                    <h5>4. 阅读动作要领，观看教学视频</h5>
                    <h5>5. 点击“开始练习”，正式开始锻炼</h5>
                    <h5>6. 如果动作准确，视频中的骨架将变成绿色，并响起提示音</h5>
                    <h4>Hope you enjoy it!</h4>
                    <p></p>
                    <div className="btn-section">
                        <Link to='/start'>
                            <button
                                className="btn start-btn"
                            >Let's Start</button>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
