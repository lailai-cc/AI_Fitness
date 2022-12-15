import React, { useState } from 'react'

import { poseInstructions } from '../../utils/data'

import { poseImages, poseName } from '../../utils/pose_images'

import './Instructions.css'


export default function Instructions({ currentPose }) {

    const [instructions, setInsntructions] = useState(poseInstructions)

    return (
        <div className="instructions-container">
            <ul className="instructions-list">
                <h3>练习技巧：</h3>
                {instructions[currentPose].map((instruction) => {
                    return (
                        <li className="instruction">{instruction}</li>
                    )
                })}
            </ul>
            <video src={require('../../utils/video/' + currentPose + '.mp4').default} controls></video>
        </div>
    )
}