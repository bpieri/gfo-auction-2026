import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="GFO Auction Block", 
    layout="wide", 
    page_icon="🛢️",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    /* General App Styling */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* FIX: Force all Input Labels to be White and Bold */
    div[data-testid="stWidgetLabel"] p {
        color: #F1C40F !important;
        font-weight: 600; /* Make them slightly bold */
    }
    
    /* Yellow Metric Values */
    div[data-testid="stMetricValue"] { color: #F1C40F !important; }
    
    /* Tabs */
    button[data-baseweb="tab"] { color: #5D6D7E; background-color: transparent; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #FF4B4B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
if 'auction_data' not in st.session_state:
    st.session_state.auction_data = [
        {"ID": 1, "Location": "Victoria, Texas", "Price": 2.50, "Volume": 5000, "Term": "1 month", "User": "Seller A", "Status": "Pending"},
        {"ID": 2, "Location": "Victoria, Texas", "Price": 2.10, "Volume": 3600, "Term": "3 months", "User": "Seller B", "Status": "Accepted"},
        {"ID": 3, "Location": "Stampede, North Dakota", "Price": -4.00, "Volume": 2000, "Term": "6 months", "User": "Seller C", "Status": "Pending"},
    ]

if 'order_id_counter' not in st.session_state:
    st.session_state.order_id_counter = 4

locations = [
    "Victoria, Texas", 
    "Stampede, North Dakota", 
    "Vernal, Utah", 
    "Pelican, Louisiana", 
    "Port Mackenzie"
]

MAX_VOLUME = 30000

# --- MOBILE-FRIENDLY SUBMIT SECTION ---
with st.expander("🚀 Tap to Submit New Offer", expanded=False):
    st.write("### New Offer Entry")
    with st.form("offer_form"):
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            user_name = st.text_input("Seller Name")
        with m_col2:
            location = st.selectbox("Location", locations)
        
        r2_col1, r2_col2, r2_col3 = st.columns([1, 1, 1])
        with r2_col1:
            price = st.number_input("Diff ($)", value=0.00, step=0.05)
        with r2_col2:
            volume = st.number_input("Vol (bbl)", min_value=100, step=100)
        with r2_col3:
            term = st.selectbox("Term", ["1mo", "3mo", "6mo"])
            
        submitted = st.form_submit_button("📢 Submit Offer", use_container_width=True)
        
        if submitted:
            if user_name:
                new_offer = {
                    "ID": st.session_state.order_id_counter,
                    "Location": location,
                    "Price": price,
                    "Volume": volume,
                    "Term": term,
                    "User": user_name,
                    "Status": "Pending"
                }
                st.session_state.auction_data.append(new_offer)
                st.session_state.order_id_counter += 1
                st.toast("✅ Offer Sent to Admin!", icon="🚀")
            else:
                st.error("Name required.")

# --- ADMIN PANEL TOGGLE (SIDEBAR) ---
st.sidebar.title("Admin Control")
admin_mode = st.sidebar.checkbox("Enable Owner View")
st.sidebar.info("Use this toggle to accept/reject offers.")

# --- MAIN DASHBOARD ---
st.title("🛢️ GFO Auction Block")
st.markdown("### Sell your crude before the capacity fills up!")
st.divider()

# Convert list to DataFrame
df = pd.DataFrame(st.session_state.auction_data)

# Create tabs for locations
tabs = st.tabs(locations)

for i, loc in enumerate(locations):
    with tabs[i]:
        # Filter data for this location
        loc_data = df[df['Location'] == loc]
        
        # Calculate Capacity
        accepted_vol = loc_data[loc_data['Status'] == "Accepted"]['Volume'].sum()
        remaining = MAX_VOLUME - accepted_vol
        pct_full = min(accepted_vol / MAX_VOLUME, 1.0)
        
        # --- GAUGE VISUALIZER ---
        g_col1, g_col2 = st.columns([1, 1])
        
        with g_col1:
            # Create the Gauge Chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = accepted_vol,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "<b>Filled Capacity</b><br><span style='font-size:0.8em;color:gray'>Barrels per Day</span>"},
                gauge = {
                    'axis': {'range': [None, MAX_VOLUME], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#4b9fff"}, 
                    'bgcolor': "#262730",
                    'borderwidth': 2,
                    'bordercolor': "#464B5C",
                    'steps': [
                        {'range': [0, MAX_VOLUME], 'color': "#262730"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': MAX_VOLUME
                    }
                }
            ))
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': "white", 'family': "Arial"},
                margin=dict(l=30, r=30, t=50, b=10),
                height=250
            )
            # FIXED LINE BELOW: Added key=f"gauge_{i}"
            st.plotly_chart(fig, use_container_width=True, key=f"gauge_{i}")

        with g_col2:
            st.write("### Space Remaining")
            st.markdown(f"""
            <div style="border: 1px solid #464B5C; border-radius: 10px; padding: 20px; text-align: center; background-color: #262730;">
                <h2 style="color: #2ECC71; margin:0;">{remaining:,}</h2>
                <p style="color: #FAFAFA; margin:0;">Barrels Available</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") # Spacer
            if pct_full >= 1.0:
                st.error("⛔ LOCATION FULL")
            elif pct_full >= 0.8:
                st.warning("⚠️ NEAR CAPACITY")
            else:
                st.success("✅ OPEN FOR BIDS")

        st.divider()

        # --- ADMIN VIEW: MANAGE OFFERS ---
        if admin_mode:
            st.subheader("🛡️ Admin: Pending Offers")
            pending = loc_data[loc_data['Status'] == "Pending"]
            
            if not pending.empty:
                for index, row in pending.iterrows():
                    c_info, c_act = st.columns([3, 1])
                    with c_info:
                        st.info(f"**{row['User']}** offers **{row['Volume']} bpd** @ **${row['Price']:.2f}** ({row['Term']})")
                    with c_act:
                        # Find the actual index in the main list to update
                        real_idx = next((i for i, d in enumerate(st.session_state.auction_data) if d["ID"] == row["ID"]), None)
                        
                        col_acc, col_rej = st.columns(2)
                        if col_acc.button("✅", key=f"acc_{row['ID']}"):
                            if remaining >= row['Volume']:
                                st.session_state.auction_data[real_idx]['Status'] = "Accepted"
                                st.rerun()
                            else:
                                st.error("Not enough capacity!")
                                
                        if col_rej.button("❌", key=f"rej_{row['ID']}"):
                            st.session_state.auction_data[real_idx]['Status'] = "Rejected"
                            st.rerun()
            else:
                st.write("No pending offers.")
            st.divider()

        # --- PUBLIC VIEW: AUCTION BOARD ---
        st.subheader("Live Auction Board")
        
        visible_offers = loc_data[loc_data['Status'].isin(["Pending", "Accepted"])].sort_values(by="Price")
        
        if not visible_offers.empty:
            # Formatting for display
            display_df = visible_offers[['Status', 'Price', 'Volume', 'Term', 'User']].copy()
            
            # Apply color coding to Status
            def color_status(val):
                color = '#2ECC71' if val == 'Accepted' else '#F39C12'
                return f'color: {color}; font-weight: bold'

            st.dataframe(
                display_df.style
                .map(color_status, subset=['Status'])
                .format({"Price": "${:+.2f}", "Volume": "{:,}"}),
                width='stretch'
            )
        else:
            st.caption("No active offers on the block.")





################### OLD CODE ########################################

# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go

# # --- CONFIGURATION & STYLING ---
# st.set_page_config(
#     page_title="GFO Auction Block", 
#     layout="wide", 
#     page_icon="🛢️",
#     initial_sidebar_state="collapsed"
# )

# # Custom CSS
# st.markdown("""
#     <style>
#     .stApp { background-color: #0E1117; color: #FAFAFA; }
    
#     /* Yellow Metric Values */
#     div[data-testid="stMetricValue"] { color: #F1C40F !important; }
    
#     /* Tabs */
#     button[data-baseweb="tab"] { color: #5D6D7E; background-color: transparent; }
#     button[data-baseweb="tab"][aria-selected="true"] {
#         color: #FFFFFF !important;
#         border-bottom-color: #FF4B4B !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# # --- DATA INITIALIZATION ---
# if 'auction_data' not in st.session_state:
#     st.session_state.auction_data = [
#         {"ID": 1, "Location": "Victoria, Texas", "Price": 2.50, "Volume": 5000, "Term": "1 month", "User": "Seller A", "Status": "Pending"},
#         {"ID": 2, "Location": "Victoria, Texas", "Price": 2.10, "Volume": 3600, "Term": "3 months", "User": "Seller B", "Status": "Accepted"},
#         {"ID": 3, "Location": "Stampede, North Dakota", "Price": -4.00, "Volume": 2000, "Term": "6 months", "User": "Seller C", "Status": "Pending"},
#     ]

# if 'order_id_counter' not in st.session_state:
#     st.session_state.order_id_counter = 4

# locations = [
#     "Victoria, Texas", 
#     "Stampede, North Dakota", 
#     "Vernal, Utah", 
#     "Pelican, Louisiana", 
#     "Port Mackenzie"
# ]

# MAX_VOLUME = 30000

# # --- MOBILE-FRIENDLY SUBMIT SECTION ---
# with st.expander("🚀 Tap to Submit New Offer", expanded=False):
#     st.write("### New Offer Entry")
#     with st.form("offer_form"):
#         m_col1, m_col2 = st.columns(2)
#         with m_col1:
#             user_name = st.text_input("Seller Name")
#         with m_col2:
#             location = st.selectbox("Location", locations)
        
#         r2_col1, r2_col2, r2_col3 = st.columns([1, 1, 1])
#         with r2_col1:
#             price = st.number_input("Diff ($)", value=0.00, step=0.05)
#         with r2_col2:
#             volume = st.number_input("Vol (bbl)", min_value=100, step=100)
#         with r2_col3:
#             term = st.selectbox("Term", ["1mo", "3mo", "6mo"])
            
#         submitted = st.form_submit_button("📢 Submit Offer", use_container_width=True)
        
#         if submitted:
#             if user_name:
#                 new_offer = {
#                     "ID": st.session_state.order_id_counter,
#                     "Location": location,
#                     "Price": price,
#                     "Volume": volume,
#                     "Term": term,
#                     "User": user_name,
#                     "Status": "Pending"
#                 }
#                 st.session_state.auction_data.append(new_offer)
#                 st.session_state.order_id_counter += 1
#                 st.toast("✅ Offer Sent to Admin!", icon="🚀")
#             else:
#                 st.error("Name required.")

# # --- ADMIN PANEL TOGGLE (SIDEBAR) ---
# st.sidebar.title("Admin Control")
# admin_mode = st.sidebar.checkbox("Enable Owner View")
# st.sidebar.info("Use this toggle to accept/reject offers.")

# # --- MAIN DASHBOARD ---
# st.title("🛢️ GFO Auction Block")
# st.markdown("### Sell your crude before the capacity fills up!")
# st.divider()

# # Convert list to DataFrame
# df = pd.DataFrame(st.session_state.auction_data)

# # Create tabs for locations
# tabs = st.tabs(locations)

# for i, loc in enumerate(locations):
#     with tabs[i]:
#         # Filter data for this location
#         loc_data = df[df['Location'] == loc]
        
#         # Calculate Capacity
#         accepted_vol = loc_data[loc_data['Status'] == "Accepted"]['Volume'].sum()
#         remaining = MAX_VOLUME - accepted_vol
#         pct_full = min(accepted_vol / MAX_VOLUME, 1.0)
        
#         # --- GAUGE VISUALIZER ---
#         g_col1, g_col2 = st.columns([1, 1])
        
#         with g_col1:
#             # Create the Gauge Chart
#             fig = go.Figure(go.Indicator(
#                 mode = "gauge+number",
#                 value = accepted_vol,
#                 domain = {'x': [0, 1], 'y': [0, 1]},
#                 title = {'text': "<b>Filled Capacity</b><br><span style='font-size:0.8em;color:gray'>Barrels per Day</span>"},
#                 gauge = {
#                     'axis': {'range': [None, MAX_VOLUME], 'tickwidth': 1, 'tickcolor': "white"},
#                     'bar': {'color': "#4b9fff"},   #FF4B4B
#                     'bgcolor': "#262730",
#                     'borderwidth': 2,
#                     'bordercolor': "#464B5C",
#                     'steps': [
#                         {'range': [0, MAX_VOLUME], 'color': "#262730"}
#                     ],
#                     'threshold': {
#                         'line': {'color': "red", 'width': 4},
#                         'thickness': 0.75,
#                         'value': MAX_VOLUME
#                     }
#                 }
#             ))
            
#             fig.update_layout(
#                 paper_bgcolor="rgba(0,0,0,0)",
#                 font={'color': "white", 'family': "Arial"},
#                 margin=dict(l=30, r=30, t=50, b=10),
#                 height=250
#             )
#             # FIXED LINE BELOW: Added key=f"gauge_{i}"
#             st.plotly_chart(fig, use_container_width=True, key=f"gauge_{i}")

#         with g_col2:
#             st.write("### Space Remaining")
#             st.markdown(f"""
#             <div style="border: 1px solid #464B5C; border-radius: 10px; padding: 20px; text-align: center; background-color: #262730;">
#                 <h2 style="color: #2ECC71; margin:0;">{remaining:,}</h2>
#                 <p style="color: #FAFAFA; margin:0;">Barrels Available</p>
#             </div>
#             """, unsafe_allow_html=True)
            
#             st.write("") # Spacer
#             if pct_full >= 1.0:
#                 st.error("⛔ LOCATION FULL")
#             elif pct_full >= 0.8:
#                 st.warning("⚠️ NEAR CAPACITY")
#             else:
#                 st.success("✅ OPEN FOR BIDS")

#         st.divider()

#         # --- ADMIN VIEW: MANAGE OFFERS ---
#         if admin_mode:
#             st.subheader("🛡️ Admin: Pending Offers")
#             pending = loc_data[loc_data['Status'] == "Pending"]
            
#             if not pending.empty:
#                 for index, row in pending.iterrows():
#                     c_info, c_act = st.columns([3, 1])
#                     with c_info:
#                         st.info(f"**{row['User']}** offers **{row['Volume']} bpd** @ **${row['Price']:.2f}** ({row['Term']})")
#                     with c_act:
#                         # Find the actual index in the main list to update
#                         real_idx = next((i for i, d in enumerate(st.session_state.auction_data) if d["ID"] == row["ID"]), None)
                        
#                         col_acc, col_rej = st.columns(2)
#                         if col_acc.button("✅", key=f"acc_{row['ID']}"):
#                             if remaining >= row['Volume']:
#                                 st.session_state.auction_data[real_idx]['Status'] = "Accepted"
#                                 st.rerun()
#                             else:
#                                 st.error("Not enough capacity!")
                                
#                         if col_rej.button("❌", key=f"rej_{row['ID']}"):
#                             st.session_state.auction_data[real_idx]['Status'] = "Rejected"
#                             st.rerun()
#             else:
#                 st.write("No pending offers.")
#             st.divider()

#         # --- PUBLIC VIEW: AUCTION BOARD ---
#         st.subheader("Live Auction Board")
        
#         visible_offers = loc_data[loc_data['Status'].isin(["Pending", "Accepted"])].sort_values(by="Price")
        
#         if not visible_offers.empty:
#             # Formatting for display
#             display_df = visible_offers[['Status', 'Price', 'Volume', 'Term', 'User']].copy()
            
#             # Apply color coding to Status
#             def color_status(val):
#                 color = '#2ECC71' if val == 'Accepted' else '#F39C12'
#                 return f'color: {color}; font-weight: bold'

#             st.dataframe(
#                 display_df.style
#                 .map(color_status, subset=['Status'])
#                 .format({"Price": "${:+.2f}", "Volume": "{:,}"}),
#                 width='stretch'
#             )
#         else:
#             st.caption("No active offers on the block.")






# ########################## OLD CODE ############################################

# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go

# # --- CONFIGURATION & STYLING ---
# # st.set_page_config(page_title="GFO Auction Block", layout="wide", page_icon="🛢️")
# st.set_page_config(
#     page_title="GFO Auction Block",
#     layout="wide",
#     page_icon="🛢️",
#     initial_sidebar_state="collapsed" # <--- ADD THIS
# )
# # Custom CSS
# st.markdown("""
#     <style>
#     .stApp { background-color: #0E1117; color: #FAFAFA; }

#     /* Yellow Prices */
#     div[data-testid="stMetricValue"] { color: #F1C40F !important; }

#     /* Tabs */
#     button[data-baseweb="tab"] { color: #5D6D7E; background-color: transparent; }
#     button[data-baseweb="tab"][aria-selected="true"] {
#         color: #FFFFFF !important;
#         border-bottom-color: #FF4B4B !important;
#     }

#     /* Progress Bar Color */
#     .stProgress > div > div > div > div { background-color: #FF4B4B; }
#     </style>
#     """, unsafe_allow_html=True)

# # --- DATA INITIALIZATION ---
# if 'auction_data' not in st.session_state:
#     st.session_state.auction_data = [
#         {"ID": 1, "Location": "Victoria, Texas", "Price": 2.50, "Volume": 5000, "Term": "1 month", "User": "Seller A",
#          "Status": "Pending"},
#         {"ID": 2, "Location": "Victoria, Texas", "Price": 2.10, "Volume": 6000, "Term": "3 months", "User": "Seller B",
#          "Status": "Accepted"},
#         {"ID": 3, "Location": "Stampede, North Dakota", "Price": -4.00, "Volume": 2000, "Term": "6 months",
#          "User": "Seller C", "Status": "Pending"},
#     ]

# if 'order_id_counter' not in st.session_state:
#     st.session_state.order_id_counter = 4

# locations = [
#     "Victoria, Texas",
#     "Stampede, North Dakota",
#     "Vernal, Utah",
#     "Pelican, Louisiana",
#     "Port Mackenzie"
# ]

# MAX_VOLUME = 30000

# # --- SIDEBAR: SELLER ENTRY ---
# # st.sidebar.title("🚀 Sell Crude Oil")
# # st.sidebar.markdown("Submit your offer to the auction block.")
# #
# # with st.sidebar.form("offer_form"):
# #     st.write("### New Offer Entry")
# #     user_name = st.text_input("Seller Name")
# #     location = st.selectbox("Delivery Location", locations)
# #
# #     col1, col2 = st.columns(2)
# #     with col1:
# #         price = st.number_input("NYMEX Differential ($)", value=0.00, step=0.05, format="%.2f")
# #     with col2:
# #         volume = st.number_input("Volume (bbl/day)", min_value=100, step=100)
# #
# #     term = st.selectbox("Term", ["1 month", "3 months", "6 months"])
# #     submitted = st.form_submit_button("📢 Submit Offer")
# #
# #     if submitted:
# #         if user_name:
# #             new_offer = {
# #                 "ID": st.session_state.order_id_counter,
# #                 "Location": location,
# #                 "Price": price,
# #                 "Volume": volume,
# #                 "Term": term,
# #                 "User": user_name,
# #                 "Status": "Pending"
# #             }
# #             st.session_state.auction_data.append(new_offer)
# #             st.session_state.order_id_counter += 1
# #             st.sidebar.success("Offer Sent to Admin!")
# #         else:
# #             st.sidebar.error("Name required.")

# # --- MOBILE-FRIENDLY SUBMIT SECTION ---
# # We use an expander so it doesn't take up screen space until needed
# with st.expander("🚀 Tap to Submit New Offer", expanded=False):
#     st.write("### New Offer Entry")
#     with st.form("offer_form"):
#         # Use columns for tighter packing on mobile
#         m_col1, m_col2 = st.columns(2)
#         with m_col1:
#             user_name = st.text_input("Seller Name")
#         with m_col2:
#             location = st.selectbox("Location", locations)

#         # Second row of inputs
#         r2_col1, r2_col2, r2_col3 = st.columns([1, 1, 1])
#         with r2_col1:
#             price = st.number_input("Diff ($)", value=0.00, step=0.05)
#         with r2_col2:
#             volume = st.number_input("Vol (bbl)", min_value=100, step=100)
#         with r2_col3:
#             term = st.selectbox("Term", ["1mo", "3mo", "6mo"])

#         submitted = st.form_submit_button("📢 Submit Offer", use_container_width=True)

#         if submitted:
#             if user_name:
#                 new_offer = {
#                     "ID": st.session_state.order_id_counter,
#                     "Location": location,
#                     "Price": price,
#                     "Volume": volume,
#                     "Term": term,
#                     "User": user_name,
#                     "Status": "Pending"
#                 }
#                 st.session_state.auction_data.append(new_offer)
#                 st.session_state.order_id_counter += 1
#                 # st.toast is better for mobile than st.success (pop-up notification)
#                 st.toast("✅ Offer Sent to Admin!", icon="🚀")
#             else:
#                 st.error("Name required.")



# # --- ADMIN PANEL TOGGLE ---
# st.sidebar.markdown("---")
# admin_mode = st.sidebar.checkbox("Admin Mode (Owner View)")

# # --- MAIN DASHBOARD ---
# # st.title("🛢️ GFO Auction Block")
# # st.markdown("🛢️ GFO Auction Block")
# st.markdown("### 🛢️ GFO Auction Block:  Sell your crude before the capacity fills up!")
# st.divider()

# # Convert list to DataFrame
# df = pd.DataFrame(st.session_state.auction_data)

# # Create tabs for locations
# tabs = st.tabs(locations)

# for i, loc in enumerate(locations):
#     with tabs[i]:
#         # Filter data for this location
#         loc_data = df[df['Location'] == loc]

#         # Calculate Capacity
#         accepted_vol = loc_data[loc_data['Status'] == "Accepted"]['Volume'].sum()
#         remaining = MAX_VOLUME - accepted_vol
#         pct_full = min(accepted_vol / MAX_VOLUME, 1.0)

#         # --- CAPACITY VISUALIZER ---
#         # c1, c2, c3 = st.columns([1, 2, 1])
#         # with c1:
#         #     st.metric("Filled Volume", f"{accepted_vol:,} bpd")
#         # with c2:
#         #     st.write(f"**Capacity Usage ({int(pct_full * 100)}%)**")
#         #     st.progress(pct_full)
#         # with c3:
#         #     st.metric("Remaining Space", f"{remaining:,} bpd", delta_color="normal")
#         #
#         # st.divider()

#         # --- RESPONSIVE CAPACITY VISUALIZER ---
#         # st.write(f"**Capacity Usage ({int(pct_full * 100)}%)**")
#         # st.progress(pct_full)

#         # # Use 2 columns instead of 3 for mobile readability
#         # c1, c2 = st.columns(2)
#         # with c1:
#         #     st.metric("Filled", f"{accepted_vol:,} bpd")
#         # with c2:
#         #     st.metric("Remaining", f"{remaining:,} bpd", delta_color="normal")

#         # st.divider()

#         # --- GAUGE VISUALIZER ---
#         # Create 2 columns: Gauge on left, Stats on right
#         g_col1, g_col2 = st.columns([1, 1])
        
#         with g_col1:
#             # Create the Gauge Chart
#             fig = go.Figure(go.Indicator(
#                 mode = "gauge+number",
#                 value = accepted_vol,
#                 domain = {'x': [0, 1], 'y': [0, 1]},
#                 title = {'text': "<b>Filled Capacity</b><br><span style='font-size:0.8em;color:gray'>Barrels per Day</span>"},
#                 gauge = {
#                     'axis': {'range': [None, MAX_VOLUME], 'tickwidth': 1, 'tickcolor': "white"},
#                     'bar': {'color': "#FF4B4B"},  # The needle/fill color (Red)
#                     'bgcolor': "#262730",         # Dark background for the dial
#                     'borderwidth': 2,
#                     'bordercolor': "#464B5C",
#                     'steps': [
#                         {'range': [0, MAX_VOLUME], 'color': "#262730"} # Background of the arc
#                     ],
#                     'threshold': {
#                         'line': {'color': "red", 'width': 4},
#                         'thickness': 0.75,
#                         'value': MAX_VOLUME
#                     }
#                 }
#             ))
            
#             # Make it look good in Dark Mode
#             fig.update_layout(
#                 paper_bgcolor="rgba(0,0,0,0)", # Transparent background
#                 font={'color': "white", 'family': "Arial"},
#                 margin=dict(l=30, r=30, t=50, b=10),
#                 height=250 # Keep it compact
#             )
#             st.plotly_chart(fig, use_container_width=True)

#         with g_col2:
#             st.write("### Space Remaining")
#             # We use a container to vertically center this info if needed
#             st.markdown(f"""
#             <div style="border: 1px solid #464B5C; border-radius: 10px; padding: 20px; text-align: center; background-color: #262730;">
#                 <h2 style="color: #2ECC71; margin:0;">{remaining:,}</h2>
#                 <p style="color: #FAFAFA; margin:0;">Barrels Available</p>
#             </div>
#             """, unsafe_allow_html=True)
            
#             st.write("") # Spacer
#             if pct_full >= 1.0:
#                 st.error("⛔ LOCATION FULL")
#             elif pct_full >= 0.8:
#                 st.warning("⚠️ NEAR CAPACITY")
#             else:
#                 st.success("✅ OPEN FOR BIDS")

#         st.divider()

#         # --- ADMIN VIEW: MANAGE OFFERS ---
#         if admin_mode:
#             st.subheader("🛡️ Admin: Pending Offers")
#             pending = loc_data[loc_data['Status'] == "Pending"]

#             if not pending.empty:
#                 for index, row in pending.iterrows():
#                     c_info, c_act = st.columns([3, 1])
#                     with c_info:
#                         st.info(
#                             f"**{row['User']}** offers **{row['Volume']} bpd** @ **${row['Price']:.2f}** ({row['Term']})")
#                     with c_act:
#                         # Find the actual index in the main list to update
#                         real_idx = next(
#                             (i for i, d in enumerate(st.session_state.auction_data) if d["ID"] == row["ID"]), None)

#                         col_acc, col_rej = st.columns(2)
#                         if col_acc.button("✅", key=f"acc_{row['ID']}"):
#                             if remaining >= row['Volume']:
#                                 st.session_state.auction_data[real_idx]['Status'] = "Accepted"
#                                 st.rerun()
#                             else:
#                                 st.error("Not enough capacity!")

#                         if col_rej.button("❌", key=f"rej_{row['ID']}"):
#                             st.session_state.auction_data[real_idx]['Status'] = "Rejected"
#                             st.rerun()
#             else:
#                 st.write("No pending offers.")
#             st.divider()

#         # --- PUBLIC VIEW: AUCTION BOARD ---
#         st.subheader("Live Auction Board")

#         # Sort by Price (Lowest Offer first is usually best for buyers,
#         # but in an auction, sellers might want to see who is aggressive.
#         # Let's sort by Price ascending (cheapest crude first).

#         # We show Accepted and Pending, but mark them clearly
#         visible_offers = loc_data[loc_data['Status'].isin(["Pending", "Accepted"])].sort_values(by="Price")

#         if not visible_offers.empty:
#             # Formatting for display
#             display_df = visible_offers[['Status', 'Price', 'Volume', 'Term', 'User']].copy()


#             # Apply color coding to Status using Pandas Styler
#             def color_status(val):
#                 color = '#2ECC71' if val == 'Accepted' else '#F39C12'
#                 return f'color: {color}; font-weight: bold'


#             st.dataframe(
#                 display_df.style
#                 .applymap(color_status, subset=['Status'])
#                 .format({"Price": "${:+.2f}", "Volume": "{:,}"}),
#                 use_container_width=True
#             )
#         else:
#             st.caption("No active offers on the block.")






