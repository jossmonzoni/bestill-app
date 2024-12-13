from app import db, Prayer, Praise, User, Discussion, DiscussionReply, PrayerReply, app
import datetime

# Test comment to verify changes are being saved
with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Add some initial prayers
    prayers = [
        {
            "content": "Lord, grant me the strength to face life's challenges with unwavering faith. Help me trust in Your perfect timing and divine plan.",
            "name": "Sarah",
            "timestamp": datetime.datetime.now(),
            "likes": 0
        },
        {
            "content": "Please pray for healing and comfort for those battling illness. May they feel Your presence and peace during their journey to recovery.",
            "name": "Michael",
            "timestamp": datetime.datetime.now(),
            "likes": 0
        },
        {
            "content": "Guide our youth to discover their purpose in You. Protect them from negative influences and light their path with Your wisdom.",
            "name": "Rachel",
            "timestamp": datetime.datetime.now(),
            "likes": 0
        },
        {
            "content": "Father, unite families in Your love. Heal broken relationships and help us forgive as You have forgiven us.",
            "name": "David",
            "timestamp": datetime.datetime.now(),
            "likes": 0
        }
    ]

    # Add some initial praises
    praises = [
        {
            "content": "Grateful for God's endless mercy! After months of searching, I've been blessed with a job that allows me to serve others.",
            "name": "James",
            "timestamp": datetime.datetime.now()
        },
        {
            "content": "Praising God for healing my mother's heart condition! The doctors are amazed by her recovery. Nothing is impossible with Him!",
            "name": "Emma",
            "timestamp": datetime.datetime.now()
        },
        {
            "content": "Thank you, Lord, for bringing peace to my troubled mind. Through prayer and faith, anxiety has been replaced with Your perfect peace.",
            "name": "Daniel",
            "timestamp": datetime.datetime.now()
        },
        {
            "content": "Celebrating one year of sobriety today! With God's strength and grace, transformation is possible. He makes all things new!",
            "name": "Grace",
            "timestamp": datetime.datetime.now()
        }
    ]

    # Add initial discussions
    discussions = [
        {
            "content": "How has your faith helped you overcome life's challenges? Share your testimony of God's faithfulness.",
            "name": "Thomas",
            "timestamp": datetime.datetime.now(),
            "likes": 0
        },
        {
            "content": "What Bible verse brings you the most comfort during difficult times? Mine is Philippians 4:13 - 'I can do all things through Christ who strengthens me.'",
            "name": "Hannah",
            "timestamp": datetime.datetime.now(),
            "likes": 0
        }
    ]

    # Add all prayers to database
    for prayer in prayers:
        new_prayer = Prayer(content=prayer["content"], name=prayer["name"], timestamp=prayer["timestamp"], likes=prayer["likes"])
        db.session.add(new_prayer)

    # Add all praises to database
    for praise in praises:
        new_praise = Praise(content=praise["content"], name=praise["name"], timestamp=praise["timestamp"])
        db.session.add(new_praise)

    # Add all discussions to database
    for discussion in discussions:
        new_discussion = Discussion(content=discussion["content"], name=discussion["name"], timestamp=discussion["timestamp"], likes=discussion["likes"])
        db.session.add(new_discussion)

    # Commit all changes
    db.session.commit()

    print("Database initialized with sample data!")
