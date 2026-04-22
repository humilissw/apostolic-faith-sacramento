import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

export default function Doctrines() {   

  return (
    <div>
        <div className="flex justify-center items-center h-80 bg-[url('../public/bible-vertical.jpg')] lg:bg-[url('../public/bible-edit.jpg')] bg-cover bg-center md:h-100 lg:h-100">
            <h1 className="text-white text-5xl md:text-7xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Our Beliefs
            </h1>
        </div>

    <div className="w-full p-6 lg:pl-20 lg:pr-20 xl:pl-45 xl:pr-45 flex justify-center font-noto-sans">
      <div className="w-full">
        <Accordion
          type="single"
          collapsible
          className="w-full"
          defaultValue="item-1"
        >
      <AccordionItem value="item-1">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
          <h1>THE DIVINE TRINITY</h1>
        </AccordionTrigger>
          <p className="pb-10">The Divine Trinity consists of three Persons: God the Father, Jesus Christ the Son, and the Holy Ghost, perfectly united as one. (Matthew 3:16-17; 1 John 5:7)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Father, the Son, and the Holy Ghost are separate and distinct Persons, possessing recognizable personalities and qualities, perfectly united in One. They are not to be thought of in any sense, as merely three names for one Person.

            The doctrine of the Trinity begins to develop in the first chapter of the Bible: "And God said, Let us make man in our image" (Genesis 1:26). The plural forms "us" and "our" indicate that the Godhead consists of more than one individual. Almost invariably throughout the Bible, the Hebrew word translated as "God" is Elohim, and this is the plural form.

            With the coming of Jesus Christ to earth, mankind was able to observe the mysterious reality of the Triune God as never before. In Matthew 3:16-17, we read of the cooperation of the three Persons of the Godhead at the baptism of Jesus in what is perhaps the clearest picture of the Trinity presented in Scripture.

            Matthew 28:19-20; John 14:26; 2 Corinthians 13:14
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-2">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>REPENTANCE</h1>
        </AccordionTrigger>
        <p className="pb-10">Repentance is a godly sorrow for sin with a renunciation of sin. (Isaiah 55:7; Matthew 4:17)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            Repentance is a deep, heartfelt sorrow for sin with a renunciation of sin. When one comes to the Lord to be saved, he is desperately in need of forgiveness for the sins he has committed. If these sins are not forgiven, they will take that person into a lost eternity. Knowing this moves a person to a feeling of dread and a desire to be completely forgiven, at any cost.

            The radical change which true salvation brings means that one cannot mix the old life with the new. If one is hanging on to the past, he is not ready for entrance into the Kingdom of God. Repentance is the sinner's key to Heaven—the only way he can approach God and receive divine favor. But when one turns to God with all of his heart, true repentance brings the abundant joy and peace of salvation into the life.

            2 Chronicles 7:14; Isaiah 55:7; Matthew 4:17; Luke 13:2-3; Acts 3:19; 2 Corinthians 7:10
          </p>
        </AccordionContent>
      </AccordionItem>

    <AccordionItem value="item-3">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>SALVATION</h1>
        </AccordionTrigger>
        <p className="pb-10">Salvation is the act of God's grace whereby we receive forgiveness for sins and stand before God as though we had never sinned. (Romans 5:1; 2 Corinthians 5:17)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>

            Salvation is the act of God's grace by which we receive remission of sins and stand before God as though we had never sinned. This experience is necessary to inherit eternal life in Heaven. In order to receive it, we must repent (have godly sorrow for the sins we have committed) and turn away from all sin. Then by faith we must reach out to God for mercy and forgiveness, and claim His promise of pardon.

            When Adam and Eve disobeyed God in the Garden, the entire human family became sinful in nature. From that day on, every person born on earth is a sinner by birth and needs to repent of the sins he or she has committed. The penalty for sin is death (Romans 6:23), but God provided the plan so that we can be saved. Jesus, God's Son, died in man's place that we might have forgiveness for sins through His Blood (Colossians 1:14).

            Man is a free agent, even though sinful in nature. By exercising that free will, we can reach out to God and be saved from sin by faith in God's redemptive plan. We can have the assurance that we are saved (also referred to as being born again). When the work of salvation has been done in the heart, God's Spirit witnesses with our spirit that we are children of God (Romans 8:16).

            John 1:1-13; 3:3; Acts 2:21; 10:43; 13:38-39; Romans 3:25-26; 5:1; Galatians 3:11,24
          </p>
        </AccordionContent>
      </AccordionItem>

    <AccordionItem value="item-4">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>SANCTIFICATION</h1>
        </AccordionTrigger>
        <p className="pb-10">Sanctification or Holiness, the act of God's grace whereby we are made holy, is the second definite work and is subsequent to salvation. (John 17:15-21; Hebrews 13:12)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The word sanctify means "to make holy, purify, consecrate, dedicate, cleanse, and separate." In order to be sanctified, the born-again Christian must consecrate, dedicate, and separate himself to God and His will. Then God will do His part by purifying the heart and making it holy.

            After being sanctified, the Christian has a heart that is perfect toward God, though he is still subject to the limitations due to his humanity and thus not immune to the possibility of errors in judgment or imperfections due to human frailty. Spiritual growth occurs as the sanctified person continues to apply God's Word to his heart, and strives to walk daily in God's will.

            Luke 1:74-75; John 17:15-17; 2 Corinthians 7:1; Ephesians 5:25-27; Hebrews 2:11; 12:14; 13:12; 1 Peter 1:16; 1 John 1:7
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-5">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE BAPTISM OF THE HOLY GHOST</h1>
        </AccordionTrigger>
        <p className="pb-10">The Baptism of the Holy Ghost is the enduement of power from on high upon the clean, sanctified life, and is evidenced by speaking in tongues as the Spirit gives utterance. (Luke 24:49; Acts 1:5-8; 2:1-4)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The baptism of the Holy Ghost is the experience of the Third Person of the Trinity, the Holy Spirit, coming into a person's life to give power for God's service. In order to be filled with the Holy Ghost, a person must first be born again through the experience of salvation. A second step, sanctification, occurs when the saved person goes deeper in consecration and God purges the heart from the inward nature of sin. Then, the heart is ready for the gift of the Holy Spirit.

            When one receives the gift of the Holy Ghost, He comes to live in the sanctified heart. When this infilling occurs, it is accompanied by the same sign as the disciples had on the Day of Pentecost—the speaking with "other tongues, as the Spirit gave them utterance" (Acts 2:4). The "other tongues" are a previously unlearned, recognizable language.

            Matthew 3:11; Mark 16:17; Luke 24:49; John 7:38-39; Acts 1:5-8; 2:4; 10:45-46; 19:6
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-6">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>DIVINE HEALING</h1>
        </AccordionTrigger>
        <p className="pb-10">Divine Healing of sickness is provided through the atonement. (James 5:14-16; 1 Peter 2:24)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The healing of sickness and disease is provided in the Atonement. Disease, pain, and death entered the world when Adam and Eve sinned. However, with the curse that followed sin, God gave a promise of deliverance. Isaiah said, "With his stripes we are healed" (Isaiah 53:5), looking ahead to the day when this promise would be fulfilled in Jesus' death on the Cross. With His Blood, Jesus provided not only for salvation and spiritual healing, but also for physical healing. See Matthew 8:16-17.

            When Jesus lived on earth, multitudes came to Him and were healed of all kinds of diseases and afflictions. In Hebrews 13:8 we read that Jesus Christ is the same yesterday, today, and forever. His healing power is never exhausted. As Creator of the human body, He is well able to mend and restore it. No form of illness or disease exists that He cannot heal, provided it is His will to do so and we have faith to believe.

            Exodus 15:26; Matthew 8:16; Mark 16:18; James 5:14-16; 1 Peter 2:24
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-7">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE SECOND COMING OF JESUS</h1>
        </AccordionTrigger>
        <p className="pb-10">The Second Coming of Jesus will be just as literal and visible as His going away. Acts 1:9-11. There will be two appearances under one coming: First, to catch away His waiting Bride. Matthew 24:40-44; 1 Thessalonians 4:15-17. Second, to execute judgment upon the ungodly. (2 Thessalonians 1:7-10; Jude 14-15)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
           The second coming of Jesus will be as literal as was His going away. See John 14:3; Acts 1:9-11. The general term, the "second coming of Christ," encompasses two separate events.

            First is the Rapture of the Church, when Jesus comes to catch away His waiting Bride. The word rapture means, "being carried away in body or spirit," and this is literally what will happen. This will be experienced only by those who are part of the Bride of Christ (Revelation 19:6-9). Scripture is very plain concerning the fact that no man knows the day nor the hour of the Rapture. It will be an instantaneous happening, and numerous warnings are given in Scripture concerning the dangers of neglecting to prepare for this event.

            The second part is the Revelation of Christ, when He returns with His saints to execute judgment upon the ungodly and to set up His millennial kingdom on earth.

            Matthew 24:40-44; 1 Thessalonians 4:15-17; Zechariah 14:3-4; 2 Thessalonians 1:7-10; Jude 14-15
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-8">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE GREAT TRIBULATION</h1>
        </AccordionTrigger>
        <p className="pb-10">The Great Tribulation will occur between Christ's coming for His Bride and His return in judgment. (Isaiah 26:20-21; Revelation 9 and 16)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Great Tribulation is a short interval of time immediately preceding the Revelation of Christ and the beginning of the Millennial Reign of Christ on earth. Its total length is thought to be no longer than seven years (Daniel 9:27). At or near its beginning, the Rapture of the Church will take place. At its ending, the Revelation of Christ will occur, which is when Jesus returns to earth with ten thousands of His saints. The period of time between the Rapture and the Revelation, The Great Tribulation, is also called the "time of Jacob's trouble" (Jeremiah 30:7) because the Jews will suffer in a greater measure than ever before. The severity of their suffering will cause them to cry out for their Messiah to come and deliver them. See Zechariah 13:9.

            The dominant figure of the Tribulation will be the Antichrist, a personal being with supernatural, satanic powers, who will take his seat at Jerusalem. All who dwell upon the earth whose names are not written in the Book of Life will worship him (Revelation 13:8).

            Great plagues will be sent upon the earth during this terrible time. These will include wars, civil uprisings, riots, famine, death, pestilences, rending of the universe, earthquakes, and geographical upheavals. The wrath of God will be poured out upon this earth in a time of fear and terror, and of darkness and torment beyond description. During this time, a huge portion of the earth's population will be destroyed.

            Revelation 6:1-17; 8:6-13; 9:1-21; 16:1-21
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-9">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>CHRIST'S MILLENNIAL REIGN</h1>
        </AccordionTrigger>
        <p className="pb-10">Christ's Millennial Reign is the literal 1000 years of peaceful reign by Jesus on earth. (Isaiah 11 and 35)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The thousand-year literal reign of Jesus on earth will be ushered in by the Revelation of Christ—the coming of Jesus back to earth with ten thousands of His saints at the close of the Great Tribulation. At this time, He will judge the nations that dwell upon the face of the earth and Satan will be bound. It will be a reign of peace and blessing. The curse, which fell when Adam and Eve transgressed the command of God, will be lifted from all creation and the world will enjoy Christ's righteous government. The saints of God who will return with Jesus from Heaven after the Marriage Supper of the Lamb will rule and reign with Him on earth.

            The Millennial Reign will close with the final Judgment from the Great White Throne.

            Isaiah 2:2-4; 11:6-9; 65:25; Hosea 2:18; Zechariah 14:9-20; 1 Corinthians 6:2; 2 Thessalonians 1:7-10; Jude 14-15; Revelation 3:21; 20:2-3
          </p>
        </AccordionContent>
      </AccordionItem>

<<<<<<< HEAD:src/fe/app/doctrines/page.tsx
      <AccordionItem value="item-10">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE GREAT TRIBULATION</h1>
        </AccordionTrigger>
        <p className="pb-10">The Great Tribulation will occur between Christ's coming for His Bride and His return in judgment. (Isaiah 26:20-21; Revelation 9 and 16)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Great Tribulation is a short interval of time immediately preceding the Revelation of Christ and the beginning of the Millennial Reign of Christ on earth. Its total length is thought to be no longer than seven years (Daniel 9:27). At or near its beginning, the Rapture of the Church will take place. At its ending, the Revelation of Christ will occur, which is when Jesus returns to earth with ten thousands of His saints. The period of time between the Rapture and the Revelation, The Great Tribulation, is also called the "time of Jacob's trouble" (Jeremiah 30:7) because the Jews will suffer in a greater measure than ever before. The severity of their suffering will cause them to cry out for their Messiah to come and deliver them. See Zechariah 13:9.

            The dominant figure of the Tribulation will be the Antichrist, a personal being with supernatural, satanic powers, who will take his seat at Jerusalem. All who dwell upon the earth whose names are not written in the Book of Life will worship him (Revelation 13:8).

            Great plagues will be sent upon the earth during this terrible time. These will include wars, civil uprisings, riots, famine, death, pestilences, rending of the universe, earthquakes, and geographical upheavals. The wrath of God will be poured out upon this earth in a time of fear and terror, and of darkness and torment beyond description. During this time, a huge portion of the earth's population will be destroyed.

            Revelation 6:1-17; 8:6-13; 9:1-21; 16:1-21
          </p>
        </AccordionContent>
      </AccordionItem>

=======
>>>>>>> main:src/fe/app/(main)/doctrines/page.tsx
      <AccordionItem value="item-11">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE GREAT WHITE THRONE JUDGMENT</h1>
        </AccordionTrigger>
        <p className="pb-10">The Great White Throne Judgment is the final judgment when all the wicked dead will stand before God. (Revelation 20:11-15)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            At the Great White Throne Judgment, which occurs at the end of Christ's Millennial Reign, God will assemble the wicked living and the wicked dead (the righteous dead came forth at the First Resurrection) to stand before Him. Though these may have been dead for thousands of years and their physical bodies long since returned to dust and ashes, the Almighty God will gather the fragments once again into a body. Then that person will stand on his feet before the Judge who sits upon the Great White Throne. God will pronounce final judgment on the living and the dead according to their works done during their life on earth. Since none of their names are found in the Book of Life, they will be cast into the lake of fire.

            Daniel 12:2; Acts 10:42; Revelation 20:11-15
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-12">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE NEW HEAVEN AND THE NEW EARTH</h1>
        </AccordionTrigger>
        <p className="pb-10">The New Heaven and the New Earth will replace the present heaven and earth, which will be destroyed after the Great White Throne Judgment (2 Peter 3:12-13; Revelation 21:1-3)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Word teaches that this earth which has been polluted by sin, and the existing heavens, will be destroyed by fire after the White Throne Judgment. Then God will create a new heaven and a new earth in which the righteous will dwell. The new heaven and the new earth will surpass anything which man is capable of describing. Pain, sorrow, tears, crying, and even death will forever be abolished in this place where the redeemed will dwell with God forever. The new heaven and earth will never pass away.

            Isaiah 65:17; 66:22; Matthew 24:35; 2 Peter 3:12-13; Revelation 21:1-3
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-13">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>ETERNAL HEAVEN AND ETERNAL HELL</h1>
        </AccordionTrigger>
        <p className="pb-10">Eternal Heaven and Eternal Hell are literal places of final destiny, each as eternal as the other. (Matthew 25:41-46; Luke 16:22-28)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Bible teaches that Hell is as eternal as Heaven. After life on earth, Heaven or Hell will be the eternal abode, depending upon how each person responded to God's call to salvation. There can be no preparation for eternity after death, for God has ordained that the choice is made in this life.

            Heaven is the abode of God, where the Redeemer has gone and from which He will someday come for His own. Hell was prepared for the devil and his angels, and is a place of literal, burning flame where the wicked dead will spend eternity cut off from the presence of God.

            Matthew 25:41-46; Mark 9:43-44; Luke 16:24; Revelation 14:10-11
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-14">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>MARRIAGE IS FOR LIFE</h1>
        </AccordionTrigger>
        <p className="pb-10">Marriage is a holy institution between one man and one woman that is binding before God, giving neither partner liberty to marry again as long as the first companion lives. (Mark 10:6-12; Romans 7:1-3)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Bible teaches that marriage is binding for life. Under the New Testament teachings of Christ, there is only one allowable cause for separation, and that is fornication (a sexual relationship prior to marriage). This provision was related to the Jewish tradition of betrothal. If, during the approximate one year betrothal period which preceded the physical consummation of the marriage, one of the parties committed fornication, the other party could terminate the marriage agreement. This allowance for divorce does not apply to those who have consummated their marriage today, since such unfaithfulness is regarded as adultery rather than fornication.

            In Matthew 19:4-6, Jesus restated God's plan for marriage as first recorded in Genesis 2:24. He emphasized the sacredness of this union with the instruction, "What therefore God hath joined together, let not man put asunder." While there may be occasions when a Christian is separated or divorced, no allowance is made for a person to marry again while the first companion lives.

            Matthew 5:31-32; 19:9; Mark 10:11-12; Luke 16:18; Romans 7:2-3
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-15">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>WATER BAPTISM</h1>
        </AccordionTrigger>
        <p className="pb-10">Water Baptism is by one immersion "in the name of the Father, and of the Son, and of the Holy Ghost," as Jesus commanded. (Matthew 3:16; 28:19)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            Water baptism is an important step for the person who has been born again. As a symbolic picture to the world of the new birth, baptism is done "in the name of the Father, and of the Son, and of the Holy Ghost," as Jesus commanded in Matthew 28:19. When a believer is baptized in water, he is showing to the world by an outward act that he is dead so far as his old sinful life is concerned, and that he has risen as a new creation in Christ Jesus, freed from the bondage of sin.

            Scriptures show that baptism by immersion was the intended method. The word baptism derives from the Greek word baptizo which means "to immerse; to make fully wet." The baptism of the Ethiopian eunuch recorded in Acts 8 is an example of this.

            Water baptism does not bring about salvation, because it is impossible for an outward washing to effect an inward work. While every new Christian should be baptized as soon as possible, the example of the thief on the cross reveals that if a person dies in Christ before he is able to be baptized, he will not be denied Heaven.

            Matthew 3:16; Acts 8:38-39; Romans 6:4-5; Colossians 2:12
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-16">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>RESTITUTION</h1>
        </AccordionTrigger>
        <p className="pb-10">Restitution is subsequent to salvation, wherein wrongs against our fellowmen are made right in order to have a clear conscience before God and man. (Ezekiel 33:15; Matthew 5:23-24)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The Bible teaches that wrongs against our fellowman for which one can make amends must be righted. One must "have always a conscience void of offence toward God, and toward men" (Acts 24:16).

            In order to become a Christian, a person repents of and confesses to God all wrongdoing. God, in turn, forgives him. One of the evidences of a salvation experience is the desire to straighten out the past wherever possible. Restitution includes restoring where one has defrauded, stolen, or slandered; repaying debts; and making confession.

            Leviticus 6:4; Ezekiel 33:15; Luke 19:8-9
          </p>
        </AccordionContent>
      </AccordionItem>

      <AccordionItem value="item-17">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>THE LORD'S SUPPER</h1>
        </AccordionTrigger>
        <p className="pb-10">The Lord's Supper is an institution ordained by Jesus so that we might remember His death until He returns. (Matthew 26:26-29; 1 Corinthians 11:23,26)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            Jesus instituted the Lord's Supper that His followers might "shew the Lord's death till he come" (1 Corinthians 11:26). This observance points back to Christ's death on the cross, and forward to His coming to earth again.

            The Bible instructs us that we are to examine ourselves before we partake of the emblems which represent His broken Body and Blood. The one who takes part in this ordinance must allow God to search his heart, and thus measure his life by the Word, lest he "eat this bread, and drink this cup of the Lord, unworthily."

            Matthew 26:26-29; Luke 22:17-20; 1 Corinthians 11:23-26
          </p>
        </AccordionContent>
      </AccordionItem>

    
    <AccordionItem value="item-18">
        <AccordionTrigger className="flex text-2xl lg:text-3xl cursor-pointer">
            <h1>WASHING THE DISCIPLE'S FEET</h1>
        </AccordionTrigger>
        <p className="pb-10">Washing the Disciple's Feet is practiced according to the example and commandment Jesus gave. (John 13:14-15)</p>
        <AccordionContent className="flex flex-col gap-4 text-balance">
          <p>
            The practice of believers washing one another's feet is a clear teaching of Jesus. Upon instituting this ordinance with His disciples, He said, "If I then, your Lord and Master, have washed your feet; ye also ought to wash one another's feet. For I have given you an example, that ye should do as I have done to you" (John 13:14,15).

            This ordinance, and that of the Lord's Supper, which was established at the same time, are for those who are born-again Christians. As we obey Christ's commandment, we find that the Spirit bears witness of God's approval and brings great joy, as Jesus said in John 13:17.
          </p>
        </AccordionContent>
      </AccordionItem>
      
        </Accordion>
      </div>
    </div>

    </div>
  )
}