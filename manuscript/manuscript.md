---
title: "Crackdown or Relocation? Targeted States of Exception and the Geography of Lethal Violence in Ecuador, 2024–2026"
---

# Crackdown or Relocation? Targeted States of Exception and the Geography of Lethal Violence in Ecuador, 2024–2026

*Anonymised manuscript prepared for the Journal of Quantitative Criminology*

## Abstract

**Objectives** Test whether Ecuador's territorially targeted states of exception, which place selected provinces and cantons under military-assisted policing, lowered homicide where they applied or moved it to bordering cantons.

**Methods** We coded the dates and territorial scope of the 24 executive acts on states of exception issued between January 2024 and September 2026 and merged them with record-level homicide data for 221 cantons over 93 months (40,822 deaths). Stacked difference-in-differences Poisson models compare cantons entering the regime with interior cantons never covered; a second arm treats uncovered cantons that border a covered one as exposed. We add event studies, donut and trend-adjusted specifications, a benchmark from earlier surges, an exit analysis and randomisation inference.

**Results** A conventional two-way fixed-effects model associates coverage with 40% more homicides, an artefact of the coastal provinces that concentrate 83% of deaths. Among 47 cantons that entered later, homicides fell 13% after entry (IRR 0.87, 95% CI 0.70–1.08). Decrees, however, followed surges: counts ran 62% above baseline in the preceding quarter. Dropping the six months before entry yields an IRR of 1.02 (0.76–1.38); extrapolating the pre-entry trend yields 0.53 (0.42–0.68). Bordering cantons show flat pre-trends and an IRR of 1.20 (0.83–1.73). Cantons leaving the regime showed no rebound.

**Conclusions** The data support neither a reduction in homicide beyond a return to pre-surge levels nor displacement, although moderate displacement cannot be excluded. Because decrees are timed on spikes, before–after comparisons will overstate their effect and pooled panel models will understate it.

**Keywords** States of exception · Militarised policing · Crime displacement · Homicide · Difference-in-differences · Ecuador

## Introduction

Ecuador moved in five years from one of the lowest homicide rates in South America to one of the highest in the world. Police records show 6.9 intentional homicides per 100,000 inhabitants in 2019, 46.3 in 2023 and 51.3 in 2025. The government's main response has been the state of exception, a constitutional device that suspends selected rights and authorises the armed forces to operate alongside the police. A nationwide declaration in January 2024, accompanied by the recognition of an "internal armed conflict", gave way from April of that year to a succession of decrees limited to named provinces and cantons. Between January 2024 and September 2026 the executive issued 24 acts declaring, renewing or amending a state of exception, 22 of them on security grounds. Most of the coastal lowlands have lived under the regime almost without interruption, while other territories have been added or dropped as violence shifted.

Whether this instrument works is disputed with unusual intensity and unusually little evidence. The executive credits each decree with arrests, seizures and fewer deaths. Critics, the Constitutional Court among them, answer that 2025 was the most violent year on record despite near-permanent emergency rule (International Crisis Group 2025). Both arguments rest on comparisons that cannot carry the weight placed on them. Before–after counts ignore that decrees are issued when violence is peaking. Comparisons between covered and uncovered territory ignore that coverage is aimed at the places where criminal organisations are strongest.

A further question has received no systematic attention in the Ecuadorian debate. Territorial targeting presumes that pressure applied in one place suppresses violence rather than relocating it. Research on drug enforcement in Mexico points the other way: crackdowns diverted trafficking routes and raised homicide in the municipalities that received them (Dell 2015), and the removal of leaders was followed by violence in neighbouring areas (Calderón et al. 2015; Lindo and Padilla-Romo 2018). Research on place-based policing in cities reaches the opposite conclusion, with displacement the exception and diffusion of benefits common (Guerette and Bowers 2009; Braga et al. 2019). Which pattern holds when the units are cantons, the enforcers are soldiers and the targets are organisations that run trafficking corridors is an empirical matter.

This article estimates the effect of targeted states of exception on homicide in the cantons they cover and in the uncovered cantons that border them. It makes three contributions. The first is a dated, canton-level record of every decree, built from the texts of the decrees and the rulings of the Constitutional Court, which we release with the replication files. The second is methodological. We show that entry into the regime is preceded by a sharp, short-lived rise in homicide, so that the estimate of the direct effect depends almost entirely on what one assumes would have happened to that rise. Rather than choose one assumption, we report the estimates under each and bring outside evidence to bear on which is more plausible. The third contribution is a test for spatial spillovers that keeps exposed cantons out of the comparison group, in line with recent work on difference-in-differences under interference (Butts 2021).

The study sits closest to Escaño and Pridemore (2026), who find that anti-cartel military interventions in Mexican municipalities were associated with higher homicide rates, and to Blair and Weintraub (2023), whose field experiment in Cali found little evidence that military patrols reduce crime. It differs from recent work on Ecuador, which explains the national surge through cocaine supply and port access (Daniele et al. 2026; Jaramillo-Ramón 2026; Jaramillo-Ramón et al. 2026) but does not evaluate the state response.

## Background

### The legal instrument

Articles 164 to 166 of the Ecuadorian Constitution allow the president to declare a state of exception in all or part of the national territory in cases of aggression, armed conflict, grave internal commotion, public calamity or natural disaster. A declaration lasts up to 60 days and may be renewed once for up to 30. It may suspend a closed list of rights, among them the inviolability of the home and of correspondence and the freedoms of movement, association and assembly, and it may order the deployment of the armed forces. The Constitutional Court reviews every decree of its own motion.

Executive Decree 110 of 8 January 2024 declared a nationwide state of exception after prison riots and the escape of a gang leader; Decree 111, a day later, declared an internal armed conflict and named 22 organisations as military targets. The nationwide regime lapsed on 7 April 2024. Three weeks later the executive began to issue territorially targeted decrees. The first two, covering five and then seven provinces, were struck down by the Court within days because the facts alleged did not establish an armed conflict in the legal sense (Dictamen 5-24-EE/24; Dictamen 6-24-EE/24). A third, Decree 318 of 2 July 2024, relied on grave internal commotion and was upheld in part. Every decree since has followed that template.

Table A1 in the Online Supplement lists the acts. Five features matter for the analysis. Coverage is defined by province or canton and is therefore observable at the level at which homicide is recorded. Four coastal provinces (Guayas, Manabí, Los Ríos and El Oro) appear in every targeted decree, and Santa Elena in all but the declaration of August 2025 and its renewal. Other territories entered later and at different dates: Orellana and the mining canton of Camilo Ponce Enríquez in July 2024, Quito in October 2024, Sucumbíos and La Troncal in January 2025, three cantons of Bolívar and Cotopaxi in August 2025, Esmeraldas, Santo Domingo de los Tsáchilas and the rest of Pichincha on 31 December 2025, and the rest of Azuay in June 2026. Some territories were later dropped, Orellana for good in July 2025. Finally, the decrees justify themselves by citing recent increases in violent deaths in the territories named, a point to which we return because it shapes identification.

Two decrees issued in September and October 2025 responded to road blockades during a national strike rather than to organised crime. We code them separately and exclude them from the treatment.

### Why enforcement may displace or amplify violence

Rational-choice accounts of displacement hold that offenders respond to a local increase in risk by moving their activity in space, time or method (Guerette and Bowers 2009). Reviews of place-based policing find that such movement is usually partial and often outweighed by a diffusion of benefits to nearby areas (Braga et al. 2019; Bowers and Johnson 2003). These findings come from interventions at the scale of street segments and neighbourhoods against volume crime.

Violence tied to drug trafficking differs in ways that make displacement more likely. The underlying activity, moving cocaine to port, is location-flexible within a corridor, and its returns are large enough to justify relocation costs. Dell (2015) shows that crackdowns in Mexican municipalities diverted trafficking to alternative routes and raised violence along them. Enforcement can also raise violence where it is applied. Arrests and killings of leaders weaken internal control and invite challenges from rivals (Calderón et al. 2015; Phillips 2015; Dickenson 2014), and unconditional repression gives organisations a reason to fight the state (Lessing 2017). Castillo and Kronick (2020) formalise why interdiction may increase violence by raising the value of contested territory. Studies of the militarisation of public security in Latin America find, on balance, no reduction in violence and some evidence of harm (Flores-Macías and Zarkin 2021; Blair and Weintraub 2023; Escaño and Pridemore 2026).

These literatures yield three hypotheses. Under deterrence and incapacitation, homicide falls in covered cantons (H1). Under spatial displacement, it rises in uncovered cantons adjacent to covered ones (H2). Under adaptation, any reduction fades as coverage becomes routine (H3). The alternative to H1, destabilisation, predicts an increase in covered cantons.

## Data

### Homicide

The Ministry of the Interior publishes a record for every intentional homicide registered by the National Police since 2014, with the date, canton, coordinates, weapon and presumed motive. We use the release of 20 October 2026, which covers deaths to 30 September 2026. The files were obtained from a public mirror that preserves the original spreadsheets and their checksums, because the ministry's portal refuses scripted downloads; the checksums match those recorded in the mirror's manifest. The analysis window runs from January 2019 to September 2026 and contains 40,822 deaths. We aggregate to canton-months and distinguish deaths by firearm (84% of the total) and deaths classified as femicide or family violence.

Two caveats apply. Records for the current year are revised with each release, so the 2026 counts are provisional. And classification by motive is made by police at an early stage; we use it only for a secondary outcome.

### Coverage

For each act we recorded the signing date, the nominal duration, the provinces and cantons named, and the Court's ruling, drawing on the decree texts as reproduced by a legal publisher and a national newspaper, and on the Court's rulings. Where the Court struck a decree down or excluded a canton, coverage ends on the date of the ruling. A canton-day is covered when a security decree in force names its province or the canton itself. A canton-month is coded as covered, $D_{it}=1$, when at least half of its days are covered; the share of days is retained for sensitivity analysis.

### Population and boundaries

Mid-year canton populations come from the 2024 revision of the official projections (INEC 2024), interpolated linearly to months. Canton polygons come from geoBoundaries (Runfola et al. 2020). Two cantons are neighbours when their polygons touch, with a 250-metre tolerance to absorb artefacts of simplification. The three Galápagos cantons have no neighbours.

### Coverage groups

The first month of coverage defines seven entry cohorts (Fig. 1). The *coastal core* comprises 77 cantons of Guayas, Manabí, Los Ríos, El Oro and Santa Elena, first covered in May 2024. The six *expansion cohorts* comprise 47 cantons that entered between July 2024 and June 2026. Of the 97 cantons never covered, 40 border a covered canton and 57 lie in the interior.

Table 1 shows how different these groups are. The coastal core holds under half of the population and 83% of homicides recorded since January 2024; its rate rose from 9.7 per 100,000 in 2019–2020 to 78.5 in 2023. It has been under a decree in 93% of canton-months since May 2024. The never-covered groups started lower and rose less.

**Table 1** Cantons, population and homicide by coverage group

| Group | Cantons | Population 2024 (millions) | Rate 2019–20 | Rate 2023 | Rate 2024 | Rate 2025 | Rate 2026 (Jan–Sep) | Canton-months under decree since May 2024 | Firearm share |
|---|---|---|---|---|---|---|---|---|---|
| Coastal core (first covered May 2024) | 77 | 8.56 | 9.7 | 78.5 | 66.8 | 89.7 | 80.4 | 93% | 89% |
| Expansion cohorts (Jul 2024–Jun 2026) | 47 | 5.77 | 6.3 | 22.5 | 19.4 | 20.7 | 18.3 | 30% | 67% |
| Never covered, bordering a covered canton | 40 | 1.90 | 3.8 | 8.0 | 6.1 | 9.8 | 9.1 | 0% | 40% |
| Never covered, interior | 57 | 1.74 | 3.4 | 8.3 | 6.2 | 8.2 | 7.6 | 0% | 48% |

Rates are homicides per 100,000 inhabitants per year. Source: authors' calculations from Ministry of the Interior records and INEC projections.

## Empirical strategy

### What can and cannot be identified

No untreated counterpart exists for the coastal core. Its cantons were covered almost continuously from the month after the nationwide regime ended, and nothing in the rest of the country resembles their trajectory before 2024 (Fig. 2). We therefore describe the core but draw causal estimates from the expansion cohorts, whose entry dates vary and for which interior cantons provide a comparison that can at least be tested. This is a restriction of scope. The estimates speak to the extension of the regime to new territory, which is the decision the executive faces at the margin, and not to the effect of emergency rule in Guayaquil or Manta.

### Static model

As a point of departure we estimate the model that most applied work would fit:

$$E[y_{it}\mid \cdot] = \exp\left(\alpha_i + \gamma_t + \beta D_{it} + \delta N_{it}\right) \qquad (1)$$

where $y_{it}$ is the number of homicides in canton $i$ and month $t$, $\alpha_i$ and $\gamma_t$ are canton and month effects, $D_{it}$ indicates coverage and $N_{it}$ indicates an uncovered canton with at least one covered neighbour. The model is estimated by Poisson pseudo-maximum likelihood, which is consistent under correct specification of the conditional mean whatever the distribution of the counts and accommodates the many zeros in small cantons (Santos Silva and Tenreyro 2006; Wooldridge 2023). With canton effects, a population offset would change nothing of substance. Equation (1) is biased when effects vary across cohorts or over time since entry (Goodman-Bacon 2021; de Chaisemartin and D'Haultfœuille 2023), and here it has the further defect of comparing the core with everything else.

### Stacked design for direct effects

For each expansion cohort $g$ we build a sub-panel that runs from 18 months before entry to 8 months after, or to September 2026 if that comes first. The sub-panel contains the cantons of cohort $g$ and the 57 interior never-covered cantons. Bordering cantons are left out of the comparison group because, if displacement occurs, they are affected by the treatment. The sub-panels are stacked and the model is

$$E[y_{its}\mid \cdot] = \exp\Big(\alpha_{is} + \gamma_{ts} + \sum_{k\neq -1}\theta_k\, T_{is}\,\mathbb{1}[q_{ts}=k]\Big) \qquad (2)$$

where $s$ indexes stacks, $T_{is}$ marks the entering cohort and $q_{ts}$ is the quarter relative to entry, with the quarter before entry as reference. Canton-by-stack and month-by-stack effects ensure that every comparison is made within a stack between an entering cohort and cantons never covered, which removes the contaminated comparisons of Eq. (1) (Baker et al. 2022; Wing et al. 2024). The pooled effect replaces the sum with $\theta\,T_{is}\,\mathbb{1}[t\geq g]$, and $\exp(\theta)$ is an incidence rate ratio (IRR).

Because cantons may leave the regime, $\theta$ is an intention-to-treat effect of first entry. In the stacked sample, entering cantons were under a decree in 88% of post-entry months.

Identification requires that, absent coverage, homicide in entering cantons would have changed in the same proportion as in interior cantons. We test the pre-entry coefficients jointly. Standard errors are clustered by province, the level at which most coverage is assigned, giving 24 clusters; we also report canton-clustered errors and a randomisation test that reassigns entry across cantons within each stack 499 times.

### Spillovers

The second stacked design treats exposure as the treatment. For each month $e$ in which some canton first acquires a covered neighbour, the exposed group contains the cantons first exposed in $e$ and not themselves covered; they are followed for 18 months before and after and censored if they enter the regime. The comparison group is again the interior never-covered cantons. Equation (2) is estimated with $T_{is}$ marking exposure. Sixty-three cantons contribute, including cantons of Esmeraldas, Santo Domingo and Pichincha in the 20 months during which they bordered the core without being covered.

### Counterfactuals for a treatment timed on a surge

The decrees say that they respond to recent violence, and the data agree (see Results). When treatment follows a transitory shock to the outcome, the parallel-trends assumption fails in a specific way, familiar since Ashenfelter (1978): the months just before entry are abnormal and the outcome would be expected to move back towards its earlier level without any intervention. We report three estimates that bracket the possibilities. The baseline uses all 18 pre-entry months as the comparison period. The *donut* estimates drop the last three or six pre-entry months, which is appropriate if the surge was transitory. The *trend-adjusted* estimate adds a linear term in event time for entering cantons, which is appropriate if the pre-entry divergence would have continued. The approach follows the logic of sensitivity analysis for violations of parallel trends (Rambachan and Roth 2023): the conclusion is reported as a function of the assumption.

To judge which assumption is nearer the truth we build a benchmark. For each province between mid-2020 and early 2023, before any decree of the period under study, we identify months in which the three preceding months averaged at least 40% above the province's own 15-month baseline, relative to the interior comparison group, and record the level over the following nine months.

### Exits

Finally, we exploit the lapse of coverage in July 2025. From August 2025 the regime was reinstated in Guayas, Manabí, Los Ríos and El Oro but not in Orellana, Sucumbíos, Santa Elena, Quito or Camilo Ponce Enríquez. A two-period model compares these 16 leaving cantons with the 74 staying cantons from August 2024 to December 2025, omitting July 2025. If coverage suppresses homicide, leavers should do worse.

## Results

### Descriptive patterns

Figure 2 plots homicide rates by group. The nationwide decree of early 2024 coincides with a fall in the coastal core from the peak of late 2023. The fall did not last: the core's rate was 66.8 per 100,000 in 2024 and 89.7 in 2025, a year in which nearly all of its cantons were under a decree in every month except July. The expansion cohorts are flatter, around 20 per 100,000 from 2023 onwards. The two never-covered groups move together until 2024, after which the bordering group runs slightly above the interior group (9.8 against 8.2 in 2025).

### Static estimates

Table 2 reports Eq. (1). With canton and month effects, coverage is associated with 40% more homicides (IRR 1.40, 95% CI 1.19–1.64), and region-by-month effects leave the estimate unchanged. Read causally, the decrees would be responsible for a large increase in killing. The coefficient disappears once the coastal core is excluded (IRR 1.04, 0.82–1.33), which shows that it reflects the continued deterioration of the coast relative to the rest of the country and not variation in coverage. The coefficient on bordering cantons is close to one in every column.

**Table 2** Static fixed-effects Poisson models, full canton-month panel

| Model | Under decree: IRR [95% CI] | Bordering a covered canton: IRR [95% CI] | N |
|---|---|---|---|
| (1) Canton and month FE | 1.40*** [1.19, 1.64] | 0.98 [0.75, 1.29] | 19,530 |
| (2) Region-by-month FE | 1.41*** [1.17, 1.69] | 1.06 [0.84, 1.34] | 19,438 |
| (3) Excluding coastal core | 1.04 [0.82, 1.33] | 0.99 [0.80, 1.23] | 12,370 |
| (4) Share of month under decree | 1.06 [0.77, 1.46] | 1.00 [0.81, 1.24] | 12,370 |
| (5) Excluding Quito and Guayaquil | 1.03 [0.73, 1.43] | 0.98 [0.77, 1.25] | 12,277 |

Standard errors clustered by province (24 clusters). Observations in cantons with no homicide in the period are dropped by the estimator. * p < .05, ** p < .01, *** p < .001.

### Direct effects in the expansion cohorts

Figure 3a shows the raw monthly counts in the stacked sample. Entering cantons recorded about 94 homicides a month between 18 and 4 months before entry, 139 in the three months before entry, and 89 in the nine months from entry. The comparison cantons show no such movement. Relative to them, the last pre-entry quarter stood 62% above baseline and the post-entry period stood exactly at baseline (ratio 1.00).

The event-study estimates in Fig. 3b say the same thing in another way. Relative to the quarter before entry, post-entry homicide is 32% to 47% lower, but so is homicide four to six quarters before entry. The pre-entry coefficients are jointly different from zero (χ² = 22.5, 5 df, p < .001). Parallel trends does not hold in the months leading up to a decree, and the direction of the failure is what the decrees' own recitals would lead one to expect.

Table 3 gives the pooled estimates. The baseline IRR is 0.87 (0.70–1.08; randomisation p = .58). Removing the three months before entry from the comparison period moves it to 0.95 (0.72–1.24), and removing six months to 1.02 (0.76–1.38). Under the opposite assumption, that the pre-entry divergence would have continued at its estimated slope of 3.9% a month, the IRR is 0.53 (0.42–0.68). The direct effect is therefore bounded between no change and a halving of homicide, and the data on entering cantons alone cannot choose within that range.

**Table 3** Stacked difference-in-differences estimates

| Specification | Covered cantons: IRR [95% CI] | Bordering cantons: IRR [95% CI] |
|---|---|---|
| Baseline (18 pre-entry months as comparison) | 0.87 [0.70, 1.08] | 1.20 [0.83, 1.73] |
| Standard errors clustered by canton | 0.87 [0.66, 1.15] | 1.20 [0.87, 1.65] |
| Region-by-month fixed effects | 0.82 [0.59, 1.12] | 1.32 [0.95, 1.84] |
| Excluding months −3 to −1 | 0.95 [0.72, 1.24] | 1.21 [0.80, 1.83] |
| Excluding months −6 to −1 | 1.02 [0.76, 1.38] | – |
| Linear pre-entry trend extrapolated | 0.53*** [0.42, 0.68] | – |
| Firearm homicides only | 0.69* [0.50, 0.96] | 1.14 [0.61, 2.15] |
| Non-firearm homicides | 1.09 [0.86, 1.39] | – |
| Femicide and family violence | 2.19** [1.22, 3.96] | – |
| Controls include bordering cantons | 0.80* [0.67, 0.95] | – |
| Placebo entry 12 months early | 1.15 [0.93, 1.43] | – |
| Excluding exposure cohort of May 2024 | – | 1.32 [0.93, 1.86] |
| Randomisation-inference p value (baseline) | 0.58 | 0.35 |
| Joint test of pre-entry coefficients, p value | 0.0004 | 0.64 |
| Treated cantons / control cantons | 47 / 57 | 63 / 57 |

IRR, incidence rate ratio. Standard errors clustered by province unless noted. * p < .05, ** p < .01, *** p < .001.

The benchmark from earlier surges bears on the choice. We identify 18 province-level episodes between 2020 and early 2023 with a median peak 58% above baseline, close to the 62% observed before entry. Nine months on, the median episode stood 74% above its baseline, and only two of the 18 had fallen back to within 20% of it. Surges in that period did not revert; they consolidated. Set against that record, the full return to baseline after entry looks like more than regression to the mean. The comparison has an obvious weakness, however. The years 2020 to 2023 were ones of secular escalation driven by the cocaine supply shock (Daniele et al. 2026), whereas national homicide has moved sideways since 2024, so that reversion may simply have become more common. We regard the benchmark as a reason not to dismiss a direct effect, and no more.

Other rows of Table 3 are consistent with a modest, imprecisely estimated reduction concentrated in gun violence. Firearm homicides fall by 31% (IRR 0.69, 0.50–0.96) while other homicides do not move. The estimate is larger when bordering cantons are added to the comparison group (0.80, 0.67–0.95), as one would expect if those cantons absorb some displaced violence. The placebo that shifts entry 12 months earlier gives 1.15 (0.93–1.43), reflecting the rising pre-trend. The series for femicide and family violence, which we expected to be unaffected, shows a large positive coefficient. It rests on 34 post-entry deaths and on a fall in the comparison group, and we read it as noise, but it is a warning against leaning on any subgroup result here, the firearm estimate included.

Table 4 reports the cohorts separately. Four of six point estimates are below one and none is distinguishable from it. The largest cohort, the 16 cantons of Esmeraldas, Santo Domingo and Pichincha that entered on 31 December 2025, has an IRR of 0.88 (0.69–1.13). We find no sign that effects fade within the window: the IRR for the first six months is 0.86, almost the same as for the full nine. H3 cannot be assessed beyond that horizon.

**Table 4** Direct estimates by entry cohort

| First month covered | Territory | Cantons | Homicides, 18 months before | Homicides, up to 9 months after | IRR [95% CI] |
|---|---|---|---|---|---|
| 2024-07 | Orellana; Camilo Ponce Enríquez | 5 | 179 | 111 | 1.19 [0.54, 2.61] |
| 2024-10 | Quito | 1 | 402 | 197 | 0.91 [0.63, 1.30] |
| 2025-01 | Sucumbíos; La Troncal | 8 | 368 | 118 | 0.62 [0.36, 1.09] |
| 2025-09 | La Maná; Las Naves; Echeandía | 3 | 38 | 17 | 0.71 [0.44, 1.17] |
| 2026-01 | Esmeraldas; Santo Domingo; rest of Pichincha | 16 | 794 | 345 | 0.88 [0.69, 1.13] |
| 2026-06 | Rest of Azuay | 14 | 49 | 11 | 1.06 [0.78, 1.44] |

### Spillovers to bordering cantons

Figure 4 shows the event study for exposed cantons. The pre-exposure coefficients are small and jointly indistinguishable from zero (χ² = 3.4, 5 df, p = .64), so the design passes the test that the direct design fails. After exposure the estimates scatter around one without a pattern. The pooled IRR is 1.20 (0.83–1.73; randomisation p = .35). It rises to 1.32 with region-by-month effects (0.95–1.84) or when the cohort exposed in May 2024 is excluded (0.93–1.86), and it is unchanged by the donut. A dose specification that scales exposure by the share of neighbours covered points the same way and is no more precise. In the static model the coefficient is 0.98 to 1.06. A second ring of 36 cantons, two steps from covered territory, shows no increase (IRR 0.80, 0.60–1.08).

The point estimate thus has the sign that displacement predicts, and the confidence interval admits anything from a 17% fall to a 73% rise. With 80% power the design would detect an increase of about two-thirds. Smaller displacement, of the order of the 20% point estimate, would go unnoticed. In absolute terms the stakes are limited by the low base: the exposed cantons recorded 442 homicides in their first nine months of exposure, and the point estimate implies about 66 more than expected, against roughly 118 fewer in covered cantons under the baseline. Neither figure is distinguishable from zero, and we do not report a displacement quotient because a ratio of two such quantities has no useful interpretation.

### Exits

Cantons that left the regime in mid-2025 were under a decree in 8% of the following canton-months, against continuous coverage for the stayers. Their homicides did not rise relative to the stayers; the IRR is 0.88 (0.60–1.29). Withdrawal of coverage was not followed by the rebound that a suppressive effect would produce, although the executive presumably withdrew where conditions had improved, which biases this comparison towards finding no rebound.

## Discussion

Three findings stand out. The first concerns measurement more than policy. The same data yield an estimate of +40%, of −13% or of −47% depending on a design choice that is easy to make without noticing. The pooled panel model attributes to the decrees the widening gap between the coast and the rest of Ecuador. The event study normalised on the eve of entry attributes to them a decline from a peak that the decrees were issued in response to. Neither number should be quoted as the effect of the policy. This matters beyond Ecuador, since emergency measures are by their nature adopted at moments of crisis, and evaluations of militarised interventions that rely on two-way fixed-effects models with treatment switching on and off (as much of the literature does) are exposed to both problems at once.

The second finding is that a defensible reading of the direct effect lies between zero and a moderate reduction. After entry, homicide in newly covered cantons returned to its earlier level and stayed there for the nine months we observe. It did not fall below that level. If the pre-entry surges were transitory, the decrees achieved nothing measurable; if they were the start of the kind of escalation seen on the coast between 2021 and 2023, the decrees prevented a good deal. The historical benchmark favours the second reading, the changed national context favours the first, and the exit analysis, in which losing coverage made no difference, favours the first as well. What can be said with some confidence is that the destabilisation result reported for Mexico (Dell 2015; Escaño and Pridemore 2026) is not reproduced: the upper confidence limit in every specification that addresses the timing problem is below a 40% increase, and the point estimates are at or below one. One reason may be that the Ecuadorian decrees authorise searches and patrols over wide areas and are not tied to the leadership-removal operations that have been linked to fragmentation (Calderón et al. 2015; Phillips 2015).

The third finding is the absence of detectable displacement to bordering cantons, with the caveat on power already stated. Flat pre-trends make this the most credible estimate in the article. It fits the urban hot-spots literature better than the Mexican trafficking literature, perhaps because bordering cantons in the highlands offer little to organisations whose business depends on ports and coastal roads. Displacement within the covered zone, between cantons of the coast, is a different matter that our design cannot see.

For policy, the results undercut the strongest claims on both sides. They do not show that states of exception drive violence up. Equally, they offer no support for the practice of renewing coverage indefinitely in the coastal core, where homicide in 2025 exceeded its 2023 level under nearly uninterrupted emergency rule, and they show that territories dropped from the regime fared no worse. The Constitutional Court has repeatedly asked the executive to justify each decree with evidence and to rely on ordinary powers where possible (Dictamen 5-25-EE/25). An evaluation requirement would be a natural complement: the executive already reports weekly counts in the recitals of each decree, and a pre-specified comparison with similar uncovered territory would cost little. Staggering the extension of coverage across comparable cantons, when operational constraints allow it, would turn future decrees into something close to an experiment.

### Limitations

The coastal core, where most deaths occur, is outside the causal analysis. The estimates describe the extension of the regime to places with lower violence, and the effect in Guayaquil or Durán may differ. Treatment is measured by legal coverage. We do not observe troop numbers, operations or curfews at canton level, and coverage on paper may correspond to very different intensities on the ground. Follow-up after entry is at most nine months, and three for the last cohort. The number of clusters is small, although inference by randomisation agrees with the cluster-robust results. Homicide is the only outcome; extortion and kidnapping, which the decrees also target, may respond differently and are not available at this resolution. Records for 2026 are provisional. Lastly, earlier states of exception under the previous administration (2021–2023) affected some coastal provinces in the pre-period, which bears on the benchmark episodes though not on the main comparisons.

## Conclusions

Ecuador has governed its security crisis through a territorially targeted emergency regime whose reach and timing we have reconstructed canton by canton. Extending that regime to new territory was followed by a return of homicide to the level that preceded the surge that triggered each decree, and by no detectable increase in neighbouring cantons. Whether the return was caused by the decrees cannot be settled with observational data when decrees are timed on peaks; the bounds run from no effect to a reduction of about one half, and the evidence from exits and from the coastal core leans towards the lower end. Researchers evaluating emergency measures elsewhere should expect the same structure and should report how their estimates change with the treatment of the pre-intervention surge. Governments that rely on such measures should be asked to design them so that their effects can be known.

## Data availability

All data are public. The canton-month panel, the decree database with its sources, and the code that reproduces every table and figure are available in an anonymised repository linked from the submission system.

## Compliance with ethical standards

The study uses public administrative records without personal identifiers and required no ethical approval. Funding and competing interests are declared on the title page.

## References

Ashenfelter O (1978) Estimating the effect of training programs on earnings. Rev Econ Stat 60(1):47–57. https://doi.org/10.2307/1924332

Baker AC, Larcker DF, Wang CCY (2022) How much should we trust staggered difference-in-differences estimates? J Financ Econ 144(2):370–395. https://doi.org/10.1016/j.jfineco.2022.01.004

Blair RA, Weintraub M (2023) Little evidence that military policing reduces crime or improves human security. Nat Hum Behav 7:861–873. https://doi.org/10.1038/s41562-023-01600-1

Bowers KJ, Johnson SD (2003) Measuring the geographical displacement and diffusion of benefit effects of crime prevention activity. J Quant Criminol 19(3):275–301. https://doi.org/10.1023/A:1024909009240

Braga AA, Turchan BS, Papachristos AV, Hureau DM (2019) Hot spots policing and crime reduction: an update of an ongoing systematic review and meta-analysis. J Exp Criminol 15(3):289–311. https://doi.org/10.1007/s11292-019-09372-3

Butts K (2021) Difference-in-differences estimation with spatial spillovers. arXiv preprint. https://doi.org/10.48550/arXiv.2105.03737

Calderón G, Robles G, Díaz-Cayeros A, Magaloni B (2015) The beheading of criminal organizations and the dynamics of violence in Mexico. J Confl Resolut 59(8):1455–1485. https://doi.org/10.1177/0022002715587053

Castillo JC, Kronick D (2020) The logic of violence in drug war. Am Polit Sci Rev 114(3):874–887. https://doi.org/10.1017/S0003055420000246

Corte Constitucional del Ecuador (2024a) Dictamen 5-24-EE/24, 9 May 2024. Quito

Corte Constitucional del Ecuador (2024b) Dictamen 6-24-EE/24, 13 June 2024. Quito

Corte Constitucional del Ecuador (2025) Dictamen 5-25-EE/25, 11 September 2025. Quito

Daniele G, Soliman A, Vargas J (2026) Cocaine goes bananas: global spillovers from an illicit supply shock. CEP Discussion Paper 2167. Centre for Economic Performance, London School of Economics, London

de Chaisemartin C, D'Haultfœuille X (2023) Two-way fixed effects and differences-in-differences estimators with several treatments. J Econom 236(2):105480. https://doi.org/10.1016/j.jeconom.2023.105480

Dell M (2015) Trafficking networks and the Mexican drug war. Am Econ Rev 105(6):1738–1779. https://doi.org/10.1257/aer.20121637

Dickenson M (2014) The impact of leadership removal on Mexican drug trafficking organizations. J Quant Criminol 30(4):651–676. https://doi.org/10.1007/s10940-014-9218-5

Escaño GJ, Pridemore WA (2026) The association between anti-cartel military intervention and municipal homicide rates in Mexico, 2000–2022. J Quant Criminol. https://doi.org/10.1007/s10940-026-09682-6

Flores-Macías GA, Zarkin J (2021) The militarization of law enforcement: evidence from Latin America. Perspect Polit 19(2):519–538. https://doi.org/10.1017/S1537592719003906

Goodman-Bacon A (2021) Difference-in-differences with variation in treatment timing. J Econom 225(2):254–277. https://doi.org/10.1016/j.jeconom.2021.03.014

Guerette RT, Bowers KJ (2009) Assessing the extent of crime displacement and diffusion of benefits: a review of situational crime prevention evaluations. Criminology 47(4):1331–1368. https://doi.org/10.1111/j.1745-9125.2009.00177.x

INEC (2024) Estimaciones y proyecciones de población, revisión 2024. Instituto Nacional de Estadística y Censos, Quito. https://www.ecuadorencifras.gob.ec/estimaciones-y-proyecciones-de-poblacion-revision-2024/

International Crisis Group (2025) Paradise lost? Ecuador's battle with organised crime. Latin America Report 109. International Crisis Group, Brussels

Jaramillo-Ramón JP (2026) The impact of coca-cultivation and drug trafficking arrests on homicide rates in Ecuador: a transnational-subnational study. J Illicit Econ Dev 8(2). https://doi.org/10.31389/jied.303

Jaramillo-Ramón JP, Pino-Uribe JF, Caicedo-Atehortúa JM (2026) Criminal order, ports, and coca booms: the onset, amplification, and persistence of Ecuador's territorial homicide divide (2014–2025). Research Square preprint. https://doi.org/10.21203/rs.3.rs-11380980/v1

Lessing B (2017) Making peace in drug wars: crackdowns and cartels in Latin America. Cambridge University Press, Cambridge

Lindo JM, Padilla-Romo M (2018) Kingpin approaches to fighting crime and community violence: evidence from Mexico's drug war. J Health Econ 58:253–268. https://doi.org/10.1016/j.jhealeco.2018.02.002

Ministerio del Interior (2026) Homicidios intencionales, 2014–2026 [dataset]. Datos Abiertos Ecuador, Quito. https://www.datosabiertos.gob.ec/dataset/homicidios-intencionales

Phillips BJ (2015) How does leadership decapitation affect violence? The case of drug trafficking organizations in Mexico. J Polit 77(2):324–336. https://doi.org/10.1086/680209

Rambachan A, Roth J (2023) A more credible approach to parallel trends. Rev Econ Stud 90(5):2555–2591. https://doi.org/10.1093/restud/rdad018

Runfola D, Anderson A, Baier H et al (2020) geoBoundaries: a global database of political administrative boundaries. PLoS ONE 15(4):e0231866. https://doi.org/10.1371/journal.pone.0231866

Santos Silva JMC, Tenreyro S (2006) The log of gravity. Rev Econ Stat 88(4):641–658. https://doi.org/10.1162/rest.88.4.641

Wing C, Yozwiak M, Hollingsworth A, Freedman S, Simon K (2024) Designing difference-in-difference studies with staggered treatment adoption: key concepts and practical guidelines. Annu Rev Public Health 45:485–505. https://doi.org/10.1146/annurev-publhealth-061022-050825

Wooldridge JM (2023) Simple approaches to nonlinear difference-in-differences with panel data. Econom J 26(3):C31–C66. https://doi.org/10.1093/ectj/utad016

## Figure captions

**Fig. 1** Cantons of mainland Ecuador by coverage group. The coastal core was first covered by a targeted state of exception in May 2024; expansion cohorts entered between July 2024 and June 2026

**Fig. 2** Monthly homicide rate per 100,000 inhabitants (annualised, three-month centred mean) by coverage group, January 2019 to September 2026. The shaded band marks the nationwide state of exception; the dotted line marks the first targeted decree

**Fig. 3** Homicide around first coverage by a targeted state of exception, expansion cohorts. a Monthly homicides summed over stacks in entering cantons (bars) and interior never-covered cantons (line). b Incidence rate ratios by quarter relative to entry from Eq. (2), with 95% confidence intervals from province-clustered standard errors

**Fig. 4** Homicide in uncovered cantons around the first coverage of a bordering canton. Incidence rate ratios by quarter relative to exposure from Eq. (2), with 95% confidence intervals from province-clustered standard errors
