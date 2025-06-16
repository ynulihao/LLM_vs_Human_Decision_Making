import dotenv

dotenv.load_dotenv('.ENV')

DEMO_SESSIONS = dict(
    MAIN=[
        dict(
            name='iowa_gambling_task',
            display_name="Iowa gambling task",
            num_demo_participants=30,

            card_num=4,
            random_card_order=False,
            random_penalty_distribution=False,

            init_money=2000.0,
            card_rewards=[100, 100, 50, 50],
            card_penalty_distributions=[
                [0, 0, 0, 0, 0, 150, 200, 250, 300, 350],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1250],
                [0, 0, 0, 0, 0, 25, 25, 50, 75, 75],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 250],
            ],
            reward_scaling_factor=1,

            use_bot_player=False,
            use_language_model=True,
            use_multimodal_model=False,
            save_html_image=False,

            language_model='gpt-4o',
            vlm_model='gpt-4-vision',
            system_prompt_file='system_prompt_choose.txt',
            use_role_play=False,
            role_play_prompt_file='american.txt',
            temperature=1.0,
            top_p=1,
            seed=None,

            debug=False,
            gpt_mean=-1,
            gpt_std=-1,

            total_interactions=80,
            timeout_seconds=30,
            max_workers=32,
            static_file_port=8001,
            lang='zh',
            app_sequence=['iowa_gambling_task', 'info_collector'],
        ),
        dict(
            name='cambridge_gambling_task',
            display_name="Cambridge Gambling Task",
            num_demo_participants=120,

            init_money=100.0,
            bets=[0.05, 0.25, 0.5, 0.75, 0.95], 
            reward_scaling_factor=1,

            use_bot_player=False, 
            use_oracle_player=True,
            
            use_language_model=True,
            use_multimodal_model=False,
            save_html_image=False,

            use_rotate_order=True,

            language_model='gpt-4o',
            vlm_model='gpt-4o-vision',

            system_prompt_file='system_prompt_choose.txt', 
            use_role_play=False,
            role_play_prompt_file='american.txt',
            temperature=1.0,
            top_p=None,
            seed=None,
            

            debug=False, 
            gpt_mean=-1,  
            gpt_std=-1,

            round_interactions=8,
            total_interactions=64,
            timeout_seconds=30,
            max_workers=32,
            static_file_port=8001,
            lang='zh',
            app_sequence=['cambridge_gambling_task', 'info_collector'],
        ),
        dict(
            name='wisconsin_card_sort_test_task',
            display_name="Wisconsin Card Sort Test",
            num_demo_participants=10,

            criteria_card_num=4,

            criteria_card_list=[{'color': 'red', 'shape': 'circle', 'count': 1},
                                {'color': 'green', 'shape': 'triangle', 'count': 2},
                                {'color': 'blue', 'shape': 'crosses', 'count': 3},
                                {'color': 'yellow', 'shape': 'star', 'count': 4}],
            switching_num=8,
            init_criteria='random',
            criteria_list=['color', 'shape', 'count'],
            participant_use_same_deck=True,
            display_symbols = ['☻', '❀', '$', '♡'], 
            display_colors=['red', 'green', 'blue', 'yellow'],
            prompt_replace_data={'circle': 'smiley',
                                 'triangle':'flower',
                                 'crosses': 'dollar',
                                 'star': 'heart'},
            use_fig=True,

            use_bot_player=False,  
            use_language_model=True,
            use_multimodal_model=False,
            save_html_image=False,

            use_rotate_order=True,

            language_model='gpt-4o',
            vlm_model='gpt-4o-mini',

            system_prompt_file='system_prompt_choose.txt',
            use_role_play=True,
            role_play_prompt_file='american.txt',
            temperature=1.0,
            top_p=1,
            seed=None,

            debug=False,
            gpt_mean=-1,
            gpt_std=-1,

            total_interactions=64,
            timeout_seconds=None,
            max_workers=32,
            static_file_port=8001,
            lang='en',
            app_sequence=['wisconsin_card_sort_test_task', 'info_collector'],
        ),
    ],
    TEST=[
    ]
)
