// Example response from https://elections.api.aclu.org/v2/calendar?state=ca

{
  calendar: [{
      dates: {
        date: "2018-11-06",
        early_vote_end: "2018-06-04",
        early_vote_start: "2018-05-05",
        election_date: "2018-06-05",
        registration_deadline: "2018-05-21",
        vbm_end: "2018-06-05",
        vbm_start: "2018-05-29"
      },
      type: "primary"
    },
    {
      dates: {
        early_vote_end: "2018-11-05",
        early_vote_start: "2018-10-08",
        election_date: "2018-11-06",
        registration_deadline: "2018-10-22",
        vbm_end: "2018-11-06",
        vbm_end_postmarkedby: "2018-11-06",
        vbm_end_receivedby: "2018-11-09",
        vbm_start: "2018-10-30"
      },
      type: "general"
    }
  ],
  ok: true
}
